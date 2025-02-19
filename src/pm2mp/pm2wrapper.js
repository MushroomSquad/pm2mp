const pm2 = require('pm2');

const methods = [
  'list',
  'start',
  'stop',
  'restart',
  'reload',
  'delete',
  'killDaemon',
  'describe'
];

/**
 * Обёртка для подключения к pm2 в виде промиса.
 */
const connectPM2 = () =>
  new Promise((resolve, reject) => {
    pm2.connect((err) => (err ? reject(err) : resolve()));
  });

/**
 * Обёртка для вызова метода pm2 в виде промиса.
 */
const callPM2Method = (methodName, args) =>
  new Promise((resolve, reject) => {
    pm2[methodName](args, (err, details) => {
      if (err) {
        return reject(err);
      }
      resolve(details);
    });
  });

/**
 * Основная функция для вызова метода pm2.
 * Подключается, вызывает метод и в любом случае отключается.
 */
const runMethod = async (methodName, args) => {
  try {
    await connectPM2();
    const details = await callPM2Method(methodName, args);
    return details;
  } finally {
    pm2.disconnect();
  }
};

/**
 * Генерируем объект с методами.
 * Каждый метод возвращает промис, который можно использовать через async/await или .then/.catch.
 */
const methodsObject = methods.reduce((acc, methodName) => {
  acc[methodName] = (args) => runMethod(methodName, args);
  return acc;
}, {});

module.exports = methodsObject;

