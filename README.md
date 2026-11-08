# Практическая работа №10

Мониторинг двух групп метрик и алерты.

- приложение: `sportline_http_requests_total` из ПР7, алерт смотрит прирост за минуту;
- компьютер: `windows_cpu_usage_percent`, собирает `host_monitor.py`.

Prometheus опрашивает источники раз в 5 секунд. Alertmanager рассылает Firing и Resolved: приложение в `/application`, компьютер в `/computer`, копия каждого события в `/reserve` на отдельном порту. В Grafana статусы видны на графиках (аннотации) и на панели State timeline.

## Запуск

1. Запустить Docker Desktop.
2. В `D:\Doker01\пересдача_докер\practos_7_metrics` выполнить `docker compose --profile demo up -d`.
3. В этой папке выполнить `pip install psutil` и `python host_monitor.py`, во втором окне `docker compose up -d`.
4. Открыть Grafana `http://localhost:3006/d/pr10-alerts` (`admin` / `admin`), Prometheus `http://localhost:9093`, Alertmanager `http://localhost:9094`.

## Проверка

- `docker stop pr7-traffic-1` - через минуту `SportLineNoRequests` станет Firing, `docker start pr7-traffic-1` вернет Resolved;
- `python test_cpu_load.py` - 45 секунд нагрузки на все ядра, `HighWindowsCpu` станет Firing, после окончания Resolved.

Уведомления пишутся в `webhook_events.jsonl` и выводятся в окно `host_monitor.py`.
