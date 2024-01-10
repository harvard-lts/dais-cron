const Cron = require("croner");
const fs = require("fs");
const {spawn} = require("child_process");
const dotenv = require('dotenv');
const { console: consoleLogger, skipLogs } = require('./logger/logger.js');

dotenv.config();

// Set cron intervals
second = process.env.SECOND
minute = process.env.MINUTE
hour = process.env.HOUR
day = process.env.DAY
month = process.env.MONTH
day_of_week = process.env.DAY_OF_WEEK
interval = `${second} ${minute} ${hour} ${day} ${month} ${day_of_week}`


/*    ┌──────────────── (optional) second (0 - 59)
      │ ┌────────────── minute (0 - 59)
      │ │ ┌──────────── hour (0 - 23)
      │ │ │ ┌────────── day of month (1 - 31)
      │ │ │ │ ┌──────── month (1 - 12, JAN-DEC)
      │ │ │ │ │ ┌────── day of week (0 - 6, SUN-Mon)
      │ │ │ │ │ │       (0 to 6 are Sunday to Saturday; 7 is Sunday, the same as 0)
      │ │ │ │ │ │       */
Cron(interval, {}, ()=> {
  console.log("checking for load report in dropbox");

  try {
    subprocess = spawn("/home/appuser/cron/monitor_dropbox.py")
    subprocess.stdout.on('data', (data) => { console.log(data.toString()) });
    subprocess.stderr.on('data', (data) => { console.log("ERR: " + data) });
  }
  catch (e) {
    console.log(e);
  }

});

//Set cron intervals
/* dropbox_second = process.env.DROPBOX_SECOND
dropbox_minute = process.env.DROPBOX_MINUTE
dropbox_hour = process.env.DROPBOX_HOUR
dropbox_day = process.env.DROPBOX_DAY
dropbox_month = process.env.DROPBOX_MONTH
dropbox_day_of_week = process.env.DROPBOX_DAY_OF_WEEK
dropbox_interval = `${dropbox_second} ${dropbox_minute} ${dropbox_hour} ${dropbox_day} ${dropbox_month} ${dropbox_day_of_week}`
	
Cron(dropbox_interval, {}, ()=> {
  console.log("checking missed exports in dropbox");

  try {
    subprocess = spawn("/home/appuser/cron/monitor_unprocessed_batches.py")
    subprocess.stdout.on('data', (data) => { console.log(data.toString()) });
    subprocess.stderr.on('data', (data) => { console.log("ERR: " + data) });
  }
  catch (e) {
    console.log(e);
  }

}); */
