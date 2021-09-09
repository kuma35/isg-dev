.. coding; utf-8

デプロイ
========

ご参考まで。

環境
----

- Ubuntu 20.04 LTS
- Python3.8

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

pip inatall mod_wsgiでエラー

apache2にapx2モジュールが必要だそうだ。

aptにどのファイルがあるか調べる

.. code-block:: sh

   apt install apt-file
   sudo apt-file update
   apt-file list apache2-dev | grep apxs

.. code-block:: text

   $ apt-file list apache2-dev | grep apxs
   apache2-dev: /usr/bin/apxs
   apache2-dev: /usr/bin/apxs2
   apache2-dev: /usr/share/man/man1/apxs.1.gz
   apache2-dev: /usr/share/man/man1/apxs2.1.gz
      
.. code-block:: sh

   sudo apt install apache2-dev


改めて pip install mod_wsgi

アカン！！

gccのincludeはさらっと -I/usr/include/python3.8 を指定してあるので、 aptで入れちゃえばいいようだ

sudo apt install python3-dev

.. code-block:: sh

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

mjpg-streamer
-------------

持ってきて、make; sudo make install

systemd用ファイル作成

リバースプロキシ設定
--------------------

指定のポートで待ち受ける形になるので、これを /stream にアクセスしたら
いいようにする。

proxy.confを設定して、
proxy.confと、proxy_http.conf を有効化する必要有る。(ここ重要)

www-dataのパーミッション
------------------------

plugdevグループに属してないとUSBError access denied が出ます。

isg.conf配置

udev.rules.d設定

