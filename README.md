# telegram-alert-bot
## Telegram Alert Bot

Simple alarm API for telegram bot.

Use `/create 0:00 "xxx"` to create an alart at a specific time.

When the alerts triggers, the bot will text message the alert message to the user every minute.

This will continue until the user uses `/stop 0:00` to the alert at that time or `/stopall` to all alerts.
