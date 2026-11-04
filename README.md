# Практическая работа №10

Две группы метрик: `sportline_http_requests_total` из стенда ПР7 и `windows_cpu_usage_percent` самого компьютера. Prometheus выполняет опрос раз в 5 секунд; Alertmanager отправляет Firing и Resolved на два локальных webhook. Grafana показывает метрики и состояние алертов.

## Запуск

1. Запустить Docker Desktop.
2. В `D:\Doker01\пересдача_докер\practos_7_metrics` выполнить `docker compose up -d`.
3. В этой папке выполнить `python host_monitor.py` и в другом терминале `docker compose up -d`.
4. Открыть Grafana `http://localhost:3006/d/pr10-alerts` (локальная учётная запись `admin` / `admin`), Prometheus `http://localhost:9093`, Alertmanager `http://localhost:9094`.

## Проверка

`docker stop pr7-traffic-1` останавливает запросы к приложению и вызывает `SportLineNoRequests`. `docker start pr7-traffic-1` восстанавливает трафик и переводит алерт в Resolved. Команда `python test_cpu_load.py` создаёт кратковременную настоящую нагрузку на процессор и проверяет `HighWindowsCpu`. Уведомления записываются в `webhook_events.jsonl`. Не запускай нагрузку во время другой тяжёлой работы.

Файл `Практическая_работа_10.docx` — единый отчёт. Конфигурация Prometheus, правила и маршруты Alertmanager лежат рядом с ним. Отчёт пересобирается через `make_report_10.py`.
