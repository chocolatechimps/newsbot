
//
//   user-interface.js
//   author: @chocolatechimps
//   date: 2024-10-24
//

const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { exec } = require('child_process');

function createWindow () {
  const mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  mainWindow.loadFile('index.html');
}

app.on('ready', createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

ipcMain.on('fetch-articles', (event, subreddit, category, limit) => {
  const command = `python ../newsbot.py fetch --subreddit ${subreddit} --category ${category} --limit ${limit}`;
  exec(command, (error, stdout, stderr) => {
    if (error) {
      console.error(`exec error: ${error}`);
      event.reply('fetch-articles-response', `Error: ${error.message}`);
      return;
    }
    if (stderr) {
      console.error(`stderr: ${stderr}`);
      event.reply('fetch-articles-response', `Error: ${stderr}`);
      return;
    }
    event.reply('fetch-articles-response', stdout);
  });
});

ipcMain.on('summarize-article', (event) => {
  const command = `python ../newsbot.py summarize`;
  exec(command, (error, stdout, stderr) => {
    if (error) {
      console.error(`exec error: ${error}`);
      event.reply('summarize-article-response', `Error: ${error.message}`);
      return;
    }
    if (stderr) {
      console.error(`stderr: ${stderr}`);
      event.reply('summarize-article-response', `Error: ${stderr}`);
      return;
    }
    event.reply('summarize-article-response', stdout);
  });
});
