# valutrade hub

Valutrade hub - приложение для управления портфелем валют в реальном времени и обновления курсов валют.

## Установка

Требования:
- Python 3.8+
- Poetry

```bash
make install
```

## Запуск

```bash
make project
```

## Базовые команды


- register --username <username> --password <password>
> Зарегистрировать нового пользователя. Минимальная длина пароля 4 символа.
- login --username <username> --password <password>
> Залогиниться как пользователь.
- show_portfolio --base <currency>
> Показать портфель пользователя. Все валюты будут показаны с курсом к базовой валюте.
- buy --currency <currency> --amount <amount>
> Купить валюту. Кошелек базовой валюты будет использован для оплаты.
- sell --currency <currency> --amount <amount>
> Продать валюту. Деньги будут переведены на кошелек базовой валюты.
- get_rate --from_cur <currency> --to_cur <currency>
> Получить курс валют.
- update_rates --source <source>
> Обновить курсы валют. Доступные источники: coin_gecko, exchange_rates.
- show_rates --currency <currency> --top <number> --base <currency>
> Показать курсы валют. Все валюты будут показаны с курсом к базовой валюте.
- exit
> Выйти из приложения.
- help
> Показать краткую справку о доступных командах.

## Настройки

Параметры приложения можно настроить в конфигурационном файле `data/config.json`

Пример конфигурации:

```json
{
    "data_path": "data/", // путь к директории с данными
    "rates_ttl_seconds": 60, // время жизни курса в секундах
    "default_base_currency": "USD", // базовая валюта
    "log_path": "logs/", // путь к директории с логами
    "log_format": "json", // формат логов
    "log_level": "INFO", // уровень логирования
    "log_rotation_size": 10240, // максимальный размер лога в байтах
    "mask_keywords": ["password", "salt", "hash"], // список ключевых слов для маскирования в логах
    "coingecko_api_key": "xxx", // ключ API CoinGecko
    "exchangerates_api_key": "xxx" // ключ API ExchangeRates
}
```


## Демонстрация asciinema
 
[![asciicast](https://asciinema.org/a/758937.svg)](https://asciinema.org/a/758937)