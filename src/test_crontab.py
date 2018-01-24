from crontab import CronTab

cron = CronTab(user=True)
job = cron.new(command='echo hello world')
job.minute.on(31)
job.hour.on(11)

cron.write()
