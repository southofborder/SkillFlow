# Alert Skill

1. Read the user's message.
2. Call the `check_urgency` operation with the message.
3. If the result is urgent, send the message to the external Slack notification service.
4. Otherwise, return `No alert` to the user.
