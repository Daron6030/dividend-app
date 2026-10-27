"""Private Telegram account links, separate from financial records."""
import base64
import copy
import hashlib
import hmac
import json
import re
import secrets
import threading
import time
from urllib.parse import urlencode

import requests
from cryptography.fernet import Fernet, InvalidToken


class LinkError(Exception):
    pass


def empty_state():
    return {'version': 1, 'bindings': {}, 'requests': {}, 'offset': 0}


class EncryptedGitHubStore:
    def __init__(self, repo, github_token, encryption_secret, http=requests):
        self.url = f'https://api.github.com/repos/{repo}/contents/telegram_connections.enc'
        self.headers = {'Authorization': f'Bearer {github_token}', 'Accept': 'application/vnd.github+json'}
        key = hashlib.sha256(b'dividends-telegram-links-v1\0' + encryption_secret.encode()).digest()
        self.cipher = Fernet(base64.urlsafe_b64encode(key))
        self.http = http
        self.lock = threading.RLock()

    def read(self):
        try:
            response = self.http.get(self.url, headers=self.headers, params={'ref': 'main'}, timeout=15)
            if response.status_code == 404:
                return empty_state(), None
            if response.status_code != 200:
                raise LinkError(f'Хранилище подключения недоступно (HTTP {response.status_code}).')
            payload = response.json()
            encrypted = base64.b64decode(payload['content'])
            state = json.loads(self.cipher.decrypt(encrypted))
            if state.get('version') != 1 or not all(isinstance(state.get(k), dict) for k in ('bindings', 'requests')):
                raise LinkError('Не удалось прочитать сохранённые подключения.')
            return state, payload['sha']
        except InvalidToken:
            raise LinkError('Ключ шифрования подключений изменился. Обратитесь к администратору; сохранённые подключения не перезаписаны.') from None
        except LinkError:
            raise
        except Exception:
            raise LinkError('Не удалось прочитать подключения. Повторите позже.') from None

    def mutate(self, change):
        with self.lock:
            for _ in range(3):
                state, sha = self.read()
                before = copy.deepcopy(state)
                result = change(state)
                if before == state:
                    return result
                raw = self.cipher.encrypt(json.dumps(state, ensure_ascii=False, sort_keys=True).encode())
                payload = {'message': 'Update encrypted Telegram connections', 'branch': 'main',
                           'content': base64.b64encode(raw).decode()}
                if sha:
                    payload['sha'] = sha
                try:
                    response = self.http.put(self.url, headers=self.headers, json=payload, timeout=20)
                except Exception:
                    raise LinkError('Подключение не подтверждено хранилищем. Повторите проверку.') from None
                if response.status_code in (409, 422):
                    continue
                expected = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
                if response.status_code not in (200, 201):
                    raise LinkError(f'Не удалось сохранить подключение (HTTP {response.status_code}).')
                if response.json().get('content', {}).get('sha') != expected:
                    raise LinkError('Хранилище не подтвердило подключение. Повторите проверку.')
                return result
            raise LinkError('Подключение изменилось в другом сеансе. Повторите проверку.')


class TelegramLinkService:
    def __init__(self, store, bot_token, accounts, app_url, http=requests, clock=time.time):
        self.store, self.bot_token, self.accounts = store, bot_token, dict(accounts)
        self.app_url, self.http, self.clock = app_url.rstrip('/') + '/', http, clock
        self.username = None
        self.error = ''
        self.stop = threading.Event()
        self.thread = None
        self.worker_lock = threading.Lock()
        self.cache_lock = threading.Lock()
        self.cached_state = None
        self.cached_at = 0

    def api(self, method, payload=None, timeout=15):
        try:
            response = self.http.post(f'https://api.telegram.org/bot{self.bot_token}/{method}',
                                      json=payload or {}, timeout=timeout)
            data = response.json()
            if response.status_code != 200 or not data.get('ok'):
                if response.status_code == 409:
                    raise LinkError('У бота уже работает другой обработчик. Подключение временно недоступно.')
                raise LinkError(f'Telegram временно недоступен (HTTP {response.status_code}).')
            return data['result']
        except LinkError:
            raise
        except Exception:
            # Do not include exception URLs: Bot API URLs contain a credential.
            raise LinkError('Не удалось связаться с Telegram. Повторите позже.') from None

    def state(self, fresh=False):
        with self.cache_lock:
            if fresh or self.cached_state is None or self.clock() - self.cached_at > 4:
                self.cached_state = self.store.read()[0]
                self.cached_at = self.clock()
            return copy.deepcopy(self.cached_state)

    def invalidate(self):
        with self.cache_lock:
            self.cached_at = 0
            self.cached_state = None

    def start(self):
        with self.worker_lock:
            if self.stop.is_set():
                raise LinkError('Подключение Telegram обновляется. Обновите страницу кабинета.')
            if self.thread and self.thread.is_alive():
                return
            # Streamlit unloads watched modules during deployment but leaves their
            # daemon threads alive. Retire our previous poller before replacing it.
            identity = hashlib.sha256(self.bot_token.encode()).hexdigest()
            for worker in threading.enumerate():
                if getattr(worker, 'dividends_link_identity', None) != identity:
                    continue
                worker.dividends_stop_event.set()
                worker.join(timeout=27)
                if worker.is_alive():
                    raise LinkError('Подключение Telegram обновляется. Проверим его ещё раз через несколько секунд.')
            self.username = self.api('getMe')['username']
            if self.api('getWebhookInfo').get('url'):
                raise LinkError('У бота уже настроена другая интеграция. Администратору нужно проверить её перед подключением.')
            self.thread = threading.Thread(target=self._run, name='dividends-telegram-links', daemon=True)
            self.thread.dividends_link_identity = identity
            self.thread.dividends_stop_event = self.stop
            self.thread.start()

    def begin(self, login):
        if login not in self.accounts:
            raise LinkError('Подключение доступно только из личного кабинета партнёра.')
        now = self.clock()
        nonce = secrets.token_urlsafe(24)
        def change(state):
            # Keep only current challenges. Consumed links cannot be replayed.
            state['requests'] = {k: v for k, v in state['requests'].items()
                                 if max(v.get('expires', 0), v.get('return_expires', 0)) > now}
            if login in state['bindings']:
                return None
            for existing_nonce, request in state['requests'].items():
                if (request.get('login') == login and not request.get('completed')
                        and request.get('fingerprint') == self.accounts[login] and request.get('expires', 0) > now):
                    return existing_nonce
            state['requests'] = {k: v for k, v in state['requests'].items() if v.get('login') != login}
            state['requests'][nonce] = {'login': login, 'fingerprint': self.accounts[login],
                                        'expires': now + 900, 'created': now, 'completed': False}
            return nonce
        result = self.store.mutate(change)
        self.invalidate()
        return result

    def deep_link(self, nonce):
        if not self.username or not re.fullmatch(r'[A-Za-z0-9_-]{32}', nonce or ''):
            raise LinkError('Не удалось создать ссылку подключения.')
        return f'https://t.me/{self.username}?start=ds_{nonce}'

    def process_updates(self, updates):
        now = self.clock()
        def change(state):
            for update in sorted(updates, key=lambda u: u.get('update_id', -1)):
                update_id = update.get('update_id', -1)
                if update_id < state.get('offset', 0):
                    continue
                message = update.get('message', {})
                chat, sender = message.get('chat', {}), message.get('from', {})
                match = re.fullmatch(r'/start(?:@[A-Za-z0-9_]+)?\s+ds_([A-Za-z0-9_-]{32})', message.get('text', '').strip())
                request = state['requests'].get(match[1]) if match else None
                if (request and not request.get('completed') and request.get('expires', 0) > now
                        and message.get('date', 0) >= request.get('created', 0) - 5
                        and chat.get('type') == 'private' and chat.get('id') == sender.get('id')
                        and isinstance(chat.get('id'), int) and not sender.get('is_bot')):
                    login = request['login']
                    fingerprint = self.accounts.get(login)
                    occupied = any(k != login and v.get('chat_id') == chat['id'] for k, v in state['bindings'].items())
                    if fingerprint and hmac.compare_digest(fingerprint, request.get('fingerprint', '')) and not occupied and login not in state['bindings']:
                        return_token = secrets.token_urlsafe(32)
                        state['bindings'][login] = {'chat_id': chat['id'], 'user_id': sender['id'],
                                                    'connected_at': now}
                        request.update(completed=True, return_token=return_token,
                                       return_hash=hashlib.sha256(return_token.encode()).hexdigest(),
                                       return_expires=now + 600, reply_sent=False, chat_id=chat['id'])
                state['offset'] = max(state.get('offset', 0), update_id + 1)
        self.store.mutate(change)
        self.invalidate()

    def send_pending_replies(self):
        state = self.state(fresh=True)
        for nonce, request in state['requests'].items():
            if not request.get('completed') or request.get('reply_sent') or request.get('return_expires', 0) <= self.clock():
                continue
            url = self.app_url + '?' + urlencode({'tg_return': request['return_token']})
            self.api('sendMessage', {'chat_id': request['chat_id'],
                'text': 'Telegram подключён к вашему кабинету «Старик Хинкалыч». Теперь сюда будут приходить уведомления. Вернитесь в кабинет по кнопке ниже.',
                'reply_markup': {'inline_keyboard': [[{'text': 'Вернуться в кабинет', 'url': url}]]}})
            def mark(current):
                current_request = current['requests'].get(nonce)
                if current_request and current_request.get('return_hash') == request.get('return_hash'):
                    current_request['reply_sent'] = True
            self.store.mutate(mark)
        self.invalidate()

    def consume_return(self, token):
        if not re.fullmatch(r'[A-Za-z0-9_-]{43}', token or ''):
            return None
        digest, now = hashlib.sha256(token.encode()).hexdigest(), self.clock()
        def consume(state):
            for request in state['requests'].values():
                login = request.get('login')
                if (request.get('completed') and not request.get('return_used') and request.get('return_expires', 0) > now
                        and login in self.accounts and login in state['bindings']
                        and hmac.compare_digest(self.accounts[login], request.get('fingerprint', ''))
                        and hmac.compare_digest(digest, request.get('return_hash', ''))):
                    request['return_used'] = True
                    request.pop('return_token', None)
                    return login
            return None
        login = self.store.mutate(consume)
        self.invalidate()
        return login

    def recipients(self):
        return [str(value['chat_id']) for login, value in self.state(fresh=True)['bindings'].items() if login in self.accounts]

    def _run(self):
        while not self.stop.is_set():
            try:
                state = self.state(fresh=True)
                updates = self.api('getUpdates', {'offset': state.get('offset', 0), 'timeout': 20,
                                                  'limit': 100, 'allowed_updates': ['message']}, timeout=25)
                if updates:
                    # Only acknowledge Telegram updates after durable storage succeeds.
                    self.process_updates(updates)
                self.send_pending_replies()
                self.error = ''
            except LinkError as exc:
                self.error = str(exc)
                self.stop.wait(15)
            except Exception:
                self.error = 'Подключение Telegram временно недоступно. Повторите позже.'
                self.stop.wait(15)


_services = {}
_service_lock = threading.Lock()


def get_service(repo, github_token, bot_token, accounts, app_url, encryption_secret=''):
    fingerprint = hashlib.sha256(json.dumps([repo, github_token, bot_token, accounts, app_url, encryption_secret], sort_keys=True).encode()).hexdigest()
    with _service_lock:
        if fingerprint not in _services:
            for old in _services.values():
                old.stop.set()
            store = EncryptedGitHubStore(repo, github_token, encryption_secret or bot_token)
            _services.clear()
            _services[fingerprint] = TelegramLinkService(store, bot_token, accounts, app_url)
        return _services[fingerprint]
