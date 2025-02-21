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

const connectPM2 = () =>
  new Promise((resolve, reject) => {
    pm2.connect((err) => (err ? reject(err) : resolve()));
  });

const callPM2Method = (methodName, args) =>
  new Promise((resolve, reject) => {
    pm2[methodName](args, (err, details) => {
      if (err) {
        return reject(err);
      }
      resolve(details);
    });
  });

const runMethod = async (methodName, args) => {
  try {
    await connectPM2();
    const details = await callPM2Method(methodName, args);
    process.stdout.write(JSON.stringify({ status: 'success', data: details }));
  } catch (error) {
    process.stdout.write(JSON.stringify({ status: 'error', message: error.message }));
  } finally {
    pm2.disconnect();
    process.exit();
  }
};

const methodsObject = methods.reduce((acc, methodName) => {
  acc[methodName] = (args) => runMethod(methodName, args);
  return acc;
}, {});

module.exports = methodsObject;
