#!/usr/bin/env python3
from dynamixel_sdk import *
import socket, time, argparse, sys
ADDR_MODE=11; ADDR_TEN=64; ADDR_PROF_V=112; ADDR_GOAL=116
OP_POS=3; TEN=1; TOFF=0
def clamp(x,a,b): return a if x<a else b if x>b else x
def deg2tick(d): return int(clamp(round((d%360.0)*4095.0/360.0),0,4095))
def smooth(cur,tgt,vel,st,dt):
    st=max(1e-4,st); om=2.0/st; x=om*dt; e=1.0/(1.0+x+0.48*x*x+0.235*x*x*x)
    ch=cur-tgt; tt=cur-ch; tmp=(vel+om*ch)*dt; nv=(vel-om*tmp)*e; nvx=tt+(ch+tmp)*e
    if (tgt-cur)*(nvx-tgt)>0: return tgt,0.0
    return nvx,nv
def main():
    p=argparse.ArgumentParser(description="Jaw UDP→Dynamixel")
    p.add_argument("--dev",default="/dev/ttyUSB0"); p.add_argument("--baud",type=int,default=57600)
    p.add_argument("--id",type=int,default=1); p.add_argument("--port",type=int,default=5006)
    p.add_argument("--min_deg",type=float,default=20.0); p.add_argument("--max_deg",type=float,default=90.0)
    p.add_argument("--prof_vel",type=int,default=60); p.add_argument("--smooth",type=float,default=0.10)
    p.add_argument("--failsafe_ms",type=int,default=500)
    a=p.parse_args()
    ph=PortHandler(a.dev)
    if not ph.openPort(): print("Open port faalde"); sys.exit(1)
    if not ph.setBaudRate(a.baud): print("Baud zetten faalde"); sys.exit(1)
    pk=PacketHandler(2.0); pk.write1ByteTxRx(ph,a.id,ADDR_MODE,OP_POS)
    pk.write4ByteTxRx(ph,a.id,ADDR_PROF_V=max(1,a.prof_vel))
    pk.write1ByteTxRx(ph,a.id,ADDR_TEN,TEN)
    sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM); sock.bind(("0.0.0.0",a.port)); sock.setblocking(False)
    tgt=a.min_deg; cur=tgt; vel=0.0; last=time.time()
    try:
        prev=time.perf_counter()
        while True:
            try:
                while True:
                    d,_=sock.recvfrom(16)
                    if d:
                        last=time.time(); v=d[0]; f=v/255.0
                        tgt=a.min_deg+(a.max_deg-a.min_deg)*f
            except BlockingIOError: pass
            if (time.time()-last)*1000>a.failsafe_ms: tgt=a.min_deg
            now=time.perf_counter(); dt=max(0.0005,min(0.05,now-prev)); prev=now
            cur,vel=smooth(cur,tgt,vel,a.smooth,dt)
            pk.write4ByteTxRx(ph,a.id,ADDR_GOAL,deg2tick(cur))
            time.sleep(0.01)
    except KeyboardInterrupt: pass
    finally:
        pk.write1ByteTxRx(ph,a.id,ADDR_TEN,TOFF); ph.closePort()
if __name__=="__main__": main()
