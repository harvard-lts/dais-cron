const { createLogger, format, transports } = require('winston');
const { combine, timestamp, label, printf } = format;
const path = require('path');
const os = require('os');
const hostname = os.hostname();
const rfs = require('rotating-file-stream');
require('winston-daily-rotate-file');
const dateFormat = require('date-fns/format')

const logger = {};

logger.logLevel = process.env.APP_LOG_LEVEL || 'debug';

logger.dateFormatStr = 'yyyy-MM-dd';

logger.dateNow = dateFormat(new Date(), logger.dateFormatStr);

logger.skipRoutes = [
  "/version",
  "/healthcheck",
  "/robots.txt",
  "/favicon.ico"
];

logger.skipLogs = (req, res) => {
  let skipLogsAnswer = false;
  logger.skipRoutes.forEach(routeToSkip => {
    if (req.originalUrl && req.originalUrl.indexOf(routeToSkip) > -1) {
      skipLogsAnswer = true;
    }
  });
  return skipLogsAnswer;
}

const loggerFormat = printf(info => {
  if(info instanceof Error) {
      return `${info.timestamp} ${info.level}: ${info.message} ${info.stack}`;
  }
  return `${info.timestamp} ${info.level}: ${info.message}`;
});

// Console logs and errors write to file using winston
logger.console = createLogger({
  level: logger.logLevel,
  format: combine(
    format.splat(),
    timestamp(),
    loggerFormat
  ),
  transports: [
    new transports.DailyRotateFile(
      {
        filename: `${hostname}_console_%DATE%.log`,
        dirname: `logs`,
        dateFormat: logger.dateFormatStr,
        maxSize: '20m',
        maxFiles: '14d'
      }),
    new transports.Console({ format: format.simple() })
  ]
});

module.exports = logger;