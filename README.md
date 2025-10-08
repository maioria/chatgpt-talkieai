# TalkieAI

## 简介
[TalkieAI](https://github.com/maioria/chatgpt-talkieai) 是一个基于AI的外语学习应用，可通过语音进行聊天，语法分析，翻译。
AI可以基于CHAT-GPT, 国内可以配置chat-gpt代理或者使用[智谱开放平台](https://open.bigmodel.cn/)

## 微信小程序
![](https://aitake.oss-cn-wulanchabu.aliyuncs.com/9dcce2ab0be473a09e3c4ce28e5d7d05ca848ead92981c14fd1d7601eb7be0f8.jpg)  

## 后端
- 使用python语言开发，开发使用的版本为3.11，web框架为fastAPI，数据层框架为SQLAlchemy，语音使用azure。
## 前端
- 前端使用uniapp开发，基于vue3，可发布到网页与小程序与APP

## 项目示例图
![](https://aitake.oss-cn-wulanchabu.aliyuncs.com/c79b6648bea061d2813773075ba3349807dcaea90c9699c5cef9cfa6b894e9ad.png)
![](https://aitake.oss-cn-wulanchabu.aliyuncs.com/e7a3ad173b55dad7682d843ce1e7a424ef321bf03ac100c81ff07519b05352d0.png)
![](https://aitake.oss-cn-wulanchabu.aliyuncs.com/6a7d7ff41c5f366b43084a41e7268dcdbc32b65fd0dd976b5ec368ac28dca3cf.png)
![](https://aitake.oss-cn-wulanchabu.aliyuncs.com/70d6feeb534e9aa9748d51c8c10acc06bb00224f8a40d96a002dc434977d1524.png)
## 本地启动
```bash
# 数据库，创建一个空的数据库，.env文件配置好数据库后启动服务，服务会自动生成相应的表，并且加载默认数据
# 1.克隆本仓库；
git clone git@github.com:maioria/chatgpt-talkieai.git
cd talkieai-server
# 2.安装依赖；
pip3 install -r requirements.txt
# 3. 启动服务（需要新建.env文件并设置变量，参考.env.default）
nohup uvicorn app.main:app --host 0.0.0.0 --port 8097 &
#前端使用HBuilder直接web或者小程序运行

# 1. 安装依赖(前端只用了俩个依赖fingerprintjs2 与 recorder)
npm install
```

## nginx配置(Web)
```bash
# uniapp可以直接跨域请求服务端地址，也可通过nginx来配置反向代理
server {
        listen       80;
        listen       [::]:80;
        server_name  {server_name};
        rewrite ^(.*) https://$server_name$1 permanent;
      }

server {
        listen       443 ssl http2;
        listen       [::]:443 ssl http2;
        server_name  {server_name};
        root         {前端编译完后的路径};
        ssl_certificate "{crt}";
        ssl_certificate_key "{key}";
        ssl_session_cache shared:SSL:1m;
        ssl_session_timeout  10m;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;

        # Load configuration files for the default server block.
        location ^~ /api/ {
           proxy_pass http://localhost:8000/api/;
           proxy_set_header Host $http_host;
           proxy_connect_timeout 15s;
           proxy_send_timeout 300s;
           proxy_read_timeout 300s;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
        location / {
           try_files $uri $uri/ /index.html;
        }
    }
```

## 贡献
如果您有任何建议或意见，欢迎提出 [Issues](https://github.com/maioria/chatgpt-talkieai/issues) 或 [ Pull Request](https://github.com/maioria/chatgpt-talkieai/pulls)。
