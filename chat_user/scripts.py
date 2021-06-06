import errors as err
import hashlib
import socket
import json
import time
import sys


# recv
def recv(s, buff, t0):
    # print('in',s,buff,t0)
    while True:
        tmp = s.recv(buff)
        if len(tmp) != 0:
            break
        if time.time() > t0 + 10:
            raise err.timeouterror
    # print('tmp:',tmp)
    return tmp


# get
def get(addr, room, passwd, t, name):
    """
    tuple->addr
    str->room
    str->passwd
    float->time
    str->name
    
    return<-float/int
    0.0: 最后时间戳
    -1: 无新消息
    -2: 错误
    """
    try:
        post = {}
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(addr)
        post['head'] = 'get'
        post['room'] = room
        post['passwd'] = hashlib.sha256(passwd.encode('utf-8')).hexdigest()
        post['time'] = t
        post_jb = json.dumps(post).encode('utf-8')
        s.send(post_jb)
        get = recv(s, 1024, time.time())
        get = json.loads(get.decode('utf-8'))
        # {'head':'no'/'pass'/'unpass','conts':int}
        if get['head'] == 'pass':
            if get['conts'] == 0:
                return -1
            else:
                for i in range(get['conts']):
                    s.send('1'.encode('utf-8'))
                    get_c = recv(s, 1024, time.time())
                    get_c = json.loads(get_c.decode('utf-8'))
                    # ['name',"cont',float]
                    if get_c[0] != name:
                        print('{}: {}'.format(get_c[0], get_c[1]))
                return get_c[2]
        elif get['head'] == 'no':
            print('No such room...')
            return -2
        elif get['head'] == 'unpass':
            print('Wrong password...')
            return -2
        try:
            s.close()
        except:
            pass
    except err.timeouterror:
        try:
            s.close()
        except:
            pass
        raise
    except:
        print('\033[31mGet Error:', sys.exc_info()[0], '\033[0m')
        try:
            s.close()
        except:
            pass
        # raise#
        return -2


# checkpass
def check(addr, room, passwd):
    """
    tuple->addr
    str->room
    str->passwd
    
    return<-int
    0: 正常
    -1: 无法连接
    -2: 房间不存在
    -3: 密钥错误
    -7: 未知错误
    """
    try:
        post = {}
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(addr)
        post['head'] = 'check'
        post['room'] = room
        post['passwd'] = hashlib.sha256(passwd.encode('utf-8')).hexdigest()
        post_jb = json.dumps(post).encode('utf-8')
        s.send(post_jb)
        get = recv(s, 128, time.time())
        get = get.decode('utf-8')
        if get == 'pass':
            return 0
        elif get == 'no':
            return -2
        elif get == 'unpass':
            return -3
        try:
            s.close()
        except:
            pass
    except ConnectionRefusedError:
        try:
            s.close()
        except:
            pass
        return -1
    except err.timeouterror:
        try:
            s.close()
        except:
            pass
        raise
    except:
        print('\033[31mCheck Error:', sys.exc_info()[0], '\033[31m')
        try:
            s.close()
        except:
            pass
        # raise#
        return -7


# send
def send(addr, room, passwd, name, cont):
    """
    tuple->addr
    str->room
    str->passwd
    str->name
    str->cont
    
    return<-int
    0: 正常
    -1: 无法连接
    -2: 内容过长
    -3: 认证错误
    -7: 未知错误
    """
    try:
        if len(cont.encode('utf-8')) > 512 or len(name) > 10:
            raise err.toolongerror
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(addr)
        post = {}
        post['head'] = 'send'
        post['room'] = room
        post['passwd'] = hashlib.sha256(passwd.encode('utf-8')).hexdigest()
        post['name'] = name
        post['cont'] = cont
        post_jb = json.dumps(post).encode('utf-8')
        s.send(post_jb)
        get = recv(s, 512, time.time())
        get = json.loads(get.decode('utf-8'))
        if get['head'] == 'pass':
            try:
                s.close()
            except:
                pass
            return 0
        elif get['head'] == 'no' or get['head'] == 'unpass':
            try:
                s.close()
            except:
                pass
            return -3
        else:
            try:
                s.close()
            except:
                pass
            return -7
    except ConnectionRefusedError:
        try:
            s.close()
        except:
            pass
        return -1
    except err.toolongerror:
        try:
            s.close()
        except:
            pass
        return -2
    except err.timeouterror:
        try:
            s.close()
        except:
            pass
        raise
    except:
        print('\033[31mSend Error:', sys.exc_info()[0], '\033[31m')
        try:
            s.close()
        except:
            pass
        return -7


# creat
def creat(addr, room, passwd, n_room, n_passwd):
    """
    tuple->addr
    str->name
    str->passwd
    str->n_room
    str->n_passwd
    
    return<-int
    0: 正常
    -1: 连接错误
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(addr)
        post = {}
        post['head'] = 'creat'
        post['room'] = room
        post['passwd'] = hashlib.sha256(passwd.encode('utf-8')).hexdigest()
        post['n_room'] = n_room
        post['n_passwd'] = hashlib.sha256(n_passwd.encode('utf-8')).hexdigest()
        post_jb = json.dumps(post).encode('utf-8')
        s.send(post_jb)
        get = recv(s, 256, time.time())
        get = json.loads(get.decode('utf-8'))
        if get['head'] == 'no':
            try:
                s.close()
            except:
                pass
            return -2
        elif get['head'] == 'unpass':
            try:
                s.close()
            except:
                pass
            return -3
        elif get['head'] == 'pass':
            try:
                s.close()
            except:
                pass
            return 0
        elif get['head'] == 'fail':
            try:
                s.close()
            except:
                pass
            return -4
        else:
            try:
                s.close()
            except:
                pass
            return -7
    except ConnectionRefusedError:
        try:
            s.close()
        except:
            pass
        return -1
    except:
        print('Creat error:', sys.exc_info()[0])
        try:
            s.close()
        except:
            pass
        return -7
