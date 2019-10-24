var http = require("http")
let { PythonShell } = require('python-shell')

function log() {
  console.log(`【${new Date().toLocaleString()}】`, ...arguments)
}

let ble_list = []

function scan() {
  log('开始扫描蓝牙设备...');
  PythonShell.run('t.py', null, function (err, result) {

    if (err) {
      log('出现错误：', err);
    } else {
      try {
        let res = JSON.parse(result[0])
        if (Array.isArray(res)) {
          ble_list = res
          // log(res)
          log('扫描完成...');
        }
      } catch (ex) {
        log('出现异常：', ex)
      }
    }
    // 重新搜索
    setTimeout(() => {
      scan()
    }, 1000)
  });

}

scan()

http.createServer(function (req, res) {//回调函数
  /*
  log(req.httpVersion);
  log(req.headers);
  log(req.method);
  log(req.url);
  log(req.trailers);
  log(req.complete);
  */
  log(req.url);
  if (req.url === '/ble') {
    res.writeHead(200, { 'Content-Type': 'application/json;charset=UTF-8' })
    res.end(JSON.stringify(ble_list))
  } else if (req.url === '/scan') {
    scan()
    res.end("重新扫描")
  } else {
    res.end('404')
  }
}).listen(8321);

log('开启http://localhost:8321');