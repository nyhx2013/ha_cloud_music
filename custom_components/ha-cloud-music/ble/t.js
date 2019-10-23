var http = require("http")
let { PythonShell } = require('python-shell')

let ble_list = []

function scan() {
  console.log('开始扫描蓝牙设备...');
  PythonShell.run('t.py', null, function (err, result) {
    if (err) throw err;
    console.log('扫描完成...');
    let res = JSON.parse(result[0])
    if (Array.isArray(res)) {
      ble_list = res
      // console.log(res)
      scan()
    }
  });

}

scan()

http.createServer(function (req, res) {//回调函数
  /*
  console.log(req.httpVersion);
  console.log(req.headers);
  console.log(req.method);
  console.log(req.url);
  console.log(req.trailers);
  console.log(req.complete);
  */
  let url = new URL(req.url)
  if (url.pathname === '/ble') {
    let mac = url.searchParams.get('mac')
    let body = ble_list
    if (mac) {
      let arr = mac.split(',')
      console.log(arr)
      if (Array.isArray(arr)) {
        body = ble_list.filter(item => arr.includes(item.mac))
      }
    }
    res.writeHead(200, { 'Content-Type': 'application/json;charset=UTF-8' })
    res.end(JSON.stringify(body))
  } else {
    res.end('404')
  }
}).listen(8321);

console.log('开启http://localhost:8321');