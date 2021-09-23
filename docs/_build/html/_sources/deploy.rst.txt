.. coding; utf-8

デプロイ
========

ご参考まで。

環境
----

.. code-block:: sh

   $ uname -oprsv
   Linux 5.11.0-36-generic #40~20.04.1-Ubuntu SMP Sat Sep 18 02:14:19 UTC 2021 x86_64 GNU/Linux
  
.. code-block:: sh

   $ python3 --version
   Python 3.8.10

.. code-block:: sh

   $ pip show pyusb
   Name: pyusb
   Version: 1.2.1
   Summary: Python USB access module
   Home-page: https://pyusb.github.io/pyusb
   Author: Jonas Malaco
   Author-email: me@jonasmalaco.com
   License: UNKNOWN
   Location: /home/hideo/work/isg-dev/venv/lib/python3.8/site-packages
   Requires: 
   Required-by: 

.. code-block:: sh

   $ apachectl -v
   Server version: Apache/2.4.41 (Ubuntu)
   Server built:   2021-07-05T07:16:56

- /home/hideo/work/isg-dev django開発フォルダ
- hideo:hideo
- /home/httpd/isg 公開用フォルダ
- chmod 775, hideo:www-data
  
.. code-block:: sh

   (user hideoのまま)
   cd /home/httpd
   git clone /home/hideo/work/isg-dev/ isg
   cd /home/httpd/isg
   python3 -m venv venv
   source ./venv/bin/activate
   pip install -U pip
   pip install -r /home/hideo/work/isg-dev/requirements.txt

mod_wsgi
--------

apache側のモジュールインストール

.. code-block:: sh

   $ sudo apt install libapache2-mod-wsgi-py3

django側でインストール...

pip inatall mod_wsgiでエラー

apache2にapx2モジュールが必要だそうだ。パッケージに含まれているファイルを確認。

.. code-block:: sh

   $ sudo apt install apt-file
   $ apt-file update
   $ apt-file list apache2-dev | grep apxs

.. code-block:: text

   apache2-dev: /usr/bin/apxs
   apache2-dev: /usr/bin/apxs2
   apache2-dev: /usr/share/man/man1/apxs.1.gz
   apache2-dev: /usr/share/man/man1/apxs2.1.gz

apxs2ありますね。apache2-devパッケージをインストールすればいいようです。

.. code-block:: sh

   sudo apt install apache2-dev

改めて pip install mod_wsgi

アカン！！ gccコンパイルでコケます。

gccのincludeはさらっと -I/usr/include/python3.8 を指定してあるので、 aptで入れちゃえばいいようだ。

.. code-block:: sh

   $ sudo apt install python3-dev
   $ pip install mod_wsgi
   Collecting mod_wsgi
   Using cached mod_wsgi-4.9.0.tar.gz (497 kB)
   Building wheels for collected packages: mod-wsgi
   Building wheel for mod-wsgi (setup.py) ... done
   Created wheel for mod-wsgi: filename=mod_wsgi-4.9.0-cp38-cp38-linux_x86_64.whl size=827329 sha256=2eb654402cb314c4094f0c3fbff455fae0a84deade4184e346747bc70552b433
   Stored in directory: /home/hideo/.cache/pip/wheels/a9/a6/a7/c3be00060a5c3ed82a95818622da34c34251c426f2872e6fbe
   Successfully built mod-wsgi
   Installing collected packages: mod-wsgi
   Successfully installed mod-wsgi-4.9.0

やっと入りました。ふぅ。

マイクロソフト ウェブカメラ LifeCam HD-5000
-------------------------------------------

/etc/udev/rules.d/ に 63-ms-hd5000.rules を作成。

.. code-block:: text

   # for MS LifeCam HD-5000
   ATTRS{idVendor}=="045e",ATTRS{idProduct}=="076d",KERNEL=="video*",SYMLINK+="webcam1"
   
mjpg-streamer
-------------

.. code-block:: sh

   $ sudo apt install cmake libjpeg8-dev
   $ git clone https://github.com/jacksonliam/mjpg-streamer.git
   $ cd mjpg-streamer-experimental
   $ make

.. code-block:: sh

   $ /usr/local/bin/mjpg_streamer --version
   MJPG Streamer Version: 310b29f4a94c46652b20c4b7b6e5cf24e532af39
   
systemd用ファイル作成 /etc/systemd/system/mjpg-streamer.service

.. code-block:: ini

   [Unit]
   Description=MJPG-Streamer with /dev/video0.
   After=network.target
   After=udev.target

   [Service]
   ExecStart=/usr/local/bin/mjpg_streamer -i "/usr/local/lib/mjpg-streamer/input_uvc.so -d /dev/video0 -f 1 -r 1920x1080" -o "/usr/local/lib/mjpg-streamer/output_http.so -p 9999"

.. code-block:: sh

   sudo systemctl enable mjpg-streamer
   sudo systemctl start mjpg-streamer

リバースプロキシ設定
--------------------

mjpg-streamerは指定のポートで待ち受ける形になるので、これを /stream にアクセスしたら
いいようにする。

proxy.confを設定して、
proxyと、proxy_http を有効化する必要有る。(proxy_http ここ重要)

proxy_httpは特にconfファイルいじる必要ないが、必要。

proxy.conf

.. code-block:: apacheconf

   ProxyRequests Off
   <Proxy *>
       Require all granted
   </Proxy>
   ProxyPass /stream http://127.0.0.1:9999
   ProxyVia On

apache2 site conf
-----------------

sites-available/isg.conf

.. code-block:: apacheconf

   LoadModule wsgi_module "/home/httpd/isg/venv/lib/python3.8/site-packages/mod_wsgi/server/mod_wsgi-py38.cpython-38-x86_64-linux-gnu.so"
   WSGIPythonHome /home/httpd/isg/venv
   WSGIPythonPath /home/httpd/isg:/home/httpd/isg/venv/lib/python3.8/site-packages

   <VirtualHost *:80>
       ErrorLog ${APACHE_LOG_DIR}/error.log
       CustomLog ${APACHE_LOG_DIR}/access.log combined

       ServerName sindobook.ddns.net

       DocumentRoot /home/httpd/isg/html
       <Directory /home/httpd/isg/html>
	   Require all granted
       </Directory>

       WSGIApplicationGroup %{GLOBAL}
       WSGIScriptAlias /rocket /home/httpd/isg/rocket/rocket/wsgi.py
       <Directory /home/httpd/isg/rocket/rocket>
	   <Files wsgi.py>
	       Require all granted
	   </Files>
       </Directory>
   </VirtualHost>

LoadModule wsgi_module ... してるのでapache再起動、roloadでは既にロード済警告が出るが実用上問題無い。

ServerNameを指定してあるが、VirtualHost設定はコレだけであるので(名前解決できず)LANからIPアドレス指定で
アクセスしても結局ココにくる。

djangoでprint()しちゃったメッセージはerror.logにwsgi errorとして出力される。将来的にはちゃんとloggingするかもしれない。

www-dataのパーミッション
------------------------

plugdevグループに属してないとUSBError access denied が出ます。

isg.conf配置

udev.rules.d設定

アクセスログのタイムゾーンが+0000になる
---------------------------------------

django絡み(wsgi絡み)のログは、
djangoのsettings.pyでTZがUTCになっていた。
'Asia/Tokyo'に修正。

それ以外はシステムの設定が'Asia/Tokyo'(+0900)であるので
Apacheもそれを引き継いで +0900 で出力する。

Apache独自で設定したい場合は、envvarsに

.. code-block:: sh

   export TZ='Pacific/Honolulu'

とか設定する。(手元の環境ではPC再起動しないと反映されないことがあった)
通常はTZの設定そのものが不要。
TZに設定する値が知りたい時は、 tzselect を実行。

USBミサイルランチャー
---------------------

/etc/udev/rules.d/40-rocketlauncher.rules

.. code-block:: ini

   SUBSYSTEM=="usb", ACTION=="add", ATTR{idVendor}=="1941", ATTR{idProduct}=="8021", GROUP="plugdev", MODE="0660"
   SUBSYSTEM=="usb", ACTION=="add", ATTR{idVendor}=="0a81", ATTR{idProduct}=="0701", GROUP="plugdev", MODE="0660"
   SUBSYSTEM=="usb", ACTION=="add", ATTR{idVendor}=="1130", ATTR{idProduct}=="0202", GROUP="plugdev", MODE="0660"

今回使うのは ATTR{idVendor}=="0a81", ATTR{idProduct}=="0701" のものです。

rulesファイルの読み込みが正しく行われているかチェック
.....................................................

当初の/etc/udev/rules.d/40-rocketlauncher.rules

.. code-block:: ini

   SUBSYSTEM=="usb", ENV{DEVTYPE}=="usb_device", ACTION=="add", SYSFS{idVendor}=="1941", SYSFS{idProduct}=="8021", GROUP="plugdev", MODE="0660"
   SUBSYSTEM=="usb", ENV{DEVTYPE}=="usb_device", ACTION=="add", SYSFS{idVendor}=="0a81", SYSFS{idProduct}=="0701", GROUP="plugdev", MODE="0660"
   SUBSYSTEM=="usb", ENV{DEVTYPE}=="usb_device", ACTION=="add", SYSFS{idVendor}=="1130", SYSFS{idProduct}=="0202", GROUP="plugdev", MODE="0660"

.. code-block:: sh

   $ udevadm montor

でUSBミサイルランチャーのデバイスをチェック。今回は /dev/bus/usb/003/006 のようだ。

.. code-block:: sh

   $ sudo udevadm test $(udevadm info -n /dev/bus/usb/003/006 -q path)

上記ruleがちゃんと読み込まれているかどうかチェック。

.. code-block:: text

   (前略)
   /etc/udev/rules.d/40-rocketlauncher.rules:1 Invalid key 'SYSFS'
   /etc/udev/rules.d/40-rocketlauncher.rules:2 Invalid key 'SYSFS'
   /etc/udev/rules.d/40-rocketlauncher.rules:3 Invalid key 'SYSFS'
   (後略)

あかん。コケとる。

どう設定すればいいのでしょう？

.. code-block:: sh
   :emphasize-lines: 11,27

   $ udevadm info -a -p $(udevadm info -q path -n /dev/bus/usb/003/006)
   looking at device '/devices/pci0000:00/0000:00:14.0/usb3/3-2':
       KERNEL=="3-2"
       SUBSYSTEM=="usb"
       DRIVER=="usb"
       ATTR{version}==" 1.10"
       ATTR{devpath}=="2"
       ATTR{quirks}=="0x0"
       ATTR{bDeviceClass}=="00"
       ATTR{bNumInterfaces}==" 1"
       ATTR{idVendor}=="0a81"
       ATTR{speed}=="1.5"
       ATTR{avoid_reset_quirk}=="0"
       ATTR{urbnum}=="10"
       ATTR{authorized}=="1"
       ATTR{ltm_capable}=="no"
       ATTR{configuration}==""
       ATTR{tx_lanes}=="1"
       ATTR{bDeviceProtocol}=="00"
       ATTR{bConfigurationValue}=="1"
       ATTR{manufacturer}=="Dream Link"
       ATTR{devnum}=="6"
       ATTR{bNumConfigurations}=="1"
       ATTR{bmAttributes}=="a0"
       ATTR{bcdDevice}=="0001"
       ATTR{bMaxPacketSize0}=="8"
       ATTR{idProduct}=="0701"
       ATTR{rx_lanes}=="1"
       ATTR{product}=="USB Missile Launcher v1.0"
       ATTR{bMaxPower}=="100mA"
       ATTR{maxchild}=="0"
       ATTR{removable}=="removable"
       ATTR{busnum}=="3"
       ATTR{bDeviceSubClass}=="00"

ということで、SYSFS{}となっていた部分をATTR{}に修正。
