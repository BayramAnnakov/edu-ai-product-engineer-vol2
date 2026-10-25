# Воркшоп1: оптимизация агента — материалы с собой

**Результат:** я могу выбрать, проверить и обосновать одно изменение в своём workflow.

Три сообщения:

1. Сначала спросите, какую работу можно убрать: точное правило, повторно используемый результат или лишний вызов. У каждого сокращения есть граница применимости.
2. Считайте стоимость и время правильного завершённого задания. Ошибки, fallback и ручная проверка могут съесть выигрыш. Cache checkbox — гипотеза; счётчики read/write — наблюдение.
3. Разделяйте результат теста и решение владельца. Failed не становится passed. Можно оставить baseline, собрать данные или предложить ограниченный trial с ценой ошибки, лимитом, rollback и checkpoint.

## Маршрут на30–45 минут для знакомства

Это ориентир, а не измеренное время обучения.

- Откройте [разбор реальных трейсов](trace-walkthrough.md), сначала сделайте прогноз, потом смотрите цифры.
- Установите [bakeoff](../README.md#use-bakeoff-in-your-own-project) в свой проект или начните с [coding-review](examples/coding-review/README.md) / [support-triage](examples/support-triage/README.md).
- Заполните [worksheet](worksheet.md): один lever, критерии качества, цена обеих ошибок, бюджет и frozen cases.
- Запустите dev. Плохого кандидата можно остановить здесь и сохранить dev-only решение. Продолжающего кандидата заморозьте перед отдельной оценкой.
- Сохраните decision.md, policy/config и минимальный набор подтверждающих результатов.

**Одна обязательная работа:** [решение по одному своему workflow](homework.md). Все файлы служат ей; пять отдельных домашних заданий не требуются.

Материалы не выполняют платные вызовы и ничего не внедряют. Для собственных провайдеров используйте свои разрешения/бюджет и актуальную документацию. Трейсы в наборе можно читать без Langfuse и без ключей.

[Open the offline Field Notes replay](replay.html): five questions, progressive reveals, actual sanitized receipts and a downloadable own-workflow plan. Download the repository ZIP and open this HTML file locally; GitHub’s code view does not execute it. No server or account is required.
