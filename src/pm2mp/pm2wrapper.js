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
 * Wrapper for connecting to pm2 using a promise.
 */
const connectPM2 = () =>
  new Promise((resolve, reject) => {
    pm2.connect((err) => (err ? reject(err) : resolve()));
  });

/**
 * Wrapper for invoking a pm2 method using a promise.
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
 * Main function to invoke a pm2 method.
 * Connects, calls the method, and disconnects regardless of the outcome.
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
 * Generate an object with methods.
 * Each method returns a promise that can be used with async/await or .then/.catch.
 */
const methodsObject = methods.reduce((acc, methodName) => {
  acc[methodName] = (args) => runMethod(methodName, args);
  return acc;
}, {});

module.exports = methodsObject;
