Search.setIndex({docnames:["deploying/firmware","deploying/gateware","firmware/index","gateware/descriptors","gateware/flash","gateware/handlers/dfu","gateware/handlers/index","gateware/handlers/windows","gateware/index","gateware/luna","gateware/platforms/audioInterface","gateware/platforms/helpers/ice40","gateware/platforms/helpers/index","gateware/platforms/index","gettingStarted","index"],envversion:{"sphinx.domains.c":2,"sphinx.domains.changeset":1,"sphinx.domains.citation":1,"sphinx.domains.cpp":5,"sphinx.domains.index":1,"sphinx.domains.javascript":2,"sphinx.domains.math":2,"sphinx.domains.python":3,"sphinx.domains.rst":2,"sphinx.domains.std":2,"sphinx.ext.intersphinx":1,"sphinx.ext.todo":2,sphinx:56},filenames:["deploying/firmware.md","deploying/gateware.md","firmware/index.md","gateware/descriptors.md","gateware/flash.md","gateware/handlers/dfu.md","gateware/handlers/index.md","gateware/handlers/windows.md","gateware/index.md","gateware/luna.md","gateware/platforms/audioInterface.md","gateware/platforms/helpers/ice40.md","gateware/platforms/helpers/index.md","gateware/platforms/index.md","gettingStarted.md","index.md"],objects:{"dragonBoot.bootloader":[[9,1,1,"","DragonBoot"]],"dragonBoot.bootloader.DragonBoot":[[9,2,1,"","elaborate"]],"dragonBoot.dfu":[[5,1,1,"","DFUConfig"],[5,1,1,"","DFURequestHandler"],[5,1,1,"","DFUState"],[5,1,1,"","DFUStatus"]],"dragonBoot.dfu.DFURequestHandler":[[5,2,1,"","elaborate"],[5,2,1,"","generateROM"],[5,2,1,"","handlerCondition"],[5,2,1,"","printSlotInfo"]],"dragonBoot.dfu.DFUState":[[5,3,1,"","dfuIdle"],[5,3,1,"","downloadBusy"],[5,3,1,"","downloadIdle"],[5,3,1,"","downloadSync"],[5,3,1,"","error"],[5,3,1,"","uploadIdle"]],"dragonBoot.dfu.DFUStatus":[[5,3,1,"","ok"]],"dragonBoot.flash":[[4,1,1,"","SPIFlash"],[4,1,1,"","SPIFlashCmd"],[4,1,1,"","SPIFlashOp"]],"dragonBoot.flash.SPIFlash":[[4,2,1,"","elaborate"]],"dragonBoot.flash.SPIFlashCmd":[[4,3,1,"","pageProgram"],[4,3,1,"","readStatus"],[4,3,1,"","releasePowerDown"],[4,3,1,"","writeEnable"]],"dragonBoot.flash.SPIFlashOp":[[4,3,1,"","erase"],[4,3,1,"","none"],[4,3,1,"","write"]],"dragonBoot.ice40":[[11,3,1,"","BankOffset"],[11,3,1,"","BootAddress"],[11,3,1,"","BootMode"],[11,1,1,"","BootModes"],[11,3,1,"","Instruction"],[11,1,1,"","Opcodes"],[11,3,1,"","Payload"],[11,3,1,"","Slot"],[11,1,1,"","Slots"],[11,3,1,"","Special"],[11,1,1,"","SpecialOpcodes"]],"dragonBoot.ice40.BootModes":[[11,3,1,"","ColdBoot"],[11,3,1,"","SimpleBoot"],[11,3,1,"","WarmBoot"]],"dragonBoot.ice40.Opcodes":[[11,3,1,"","BankHeight"],[11,3,1,"","BankNumber"],[11,3,1,"","BankOffset"],[11,3,1,"","BankWidth"],[11,3,1,"","BootAddress"],[11,3,1,"","BootMode"],[11,3,1,"","CRCCheck"],[11,3,1,"","InternalOscRange"],[11,3,1,"","Special"]],"dragonBoot.ice40.Slots":[[11,2,1,"","_buildSlot"],[11,2,1,"","_buildSlots"],[11,2,1,"","build"]],"dragonBoot.ice40.SpecialOpcodes":[[11,3,1,"","BRAMData"],[11,3,1,"","CRAMData"],[11,3,1,"","Reboot"],[11,3,1,"","ResetCRC"],[11,3,1,"","Wakeup"]],"dragonBoot.ice40.dragonBoot.ice40.BankOffset":[[11,3,1,"","offset"]],"dragonBoot.ice40.dragonBoot.ice40.BootAddress":[[11,3,1,"","address"],[11,3,1,"","addressLength"]],"dragonBoot.ice40.dragonBoot.ice40.BootMode":[[11,3,1,"","mode"],[11,3,1,"","reserved"]],"dragonBoot.ice40.dragonBoot.ice40.BootMode.mode":[[11,3,1,"","ColdBoot"],[11,3,1,"","SimpleBoot"],[11,3,1,"","WarmBoot"]],"dragonBoot.ice40.dragonBoot.ice40.Instruction":[[11,3,1,"","byteCount"],[11,3,1,"","instruction"],[11,3,1,"","payload"]],"dragonBoot.ice40.dragonBoot.ice40.Instruction.instruction":[[11,3,1,"","BankHeight"],[11,3,1,"","BankNumber"],[11,3,1,"","BankOffset"],[11,3,1,"","BankWidth"],[11,3,1,"","BootAddress"],[11,3,1,"","BootMode"],[11,3,1,"","CRCCheck"],[11,3,1,"","InternalOscRange"],[11,3,1,"","Special"]],"dragonBoot.ice40.dragonBoot.ice40.Slot":[[11,3,1,"","bitstream"],[11,3,1,"","bitstreamMagic"]],"dragonBoot.ice40.dragonBoot.ice40.Slot.bitstream":[[11,3,1,"","GreedyRange"]],"dragonBoot.ice40.dragonBoot.ice40.Special":[[11,3,1,"","operation"]],"dragonBoot.ice40.dragonBoot.ice40.Special.operation":[[11,3,1,"","BRAMData"],[11,3,1,"","CRAMData"],[11,3,1,"","Reboot"],[11,3,1,"","ResetCRC"],[11,3,1,"","Wakeup"]],"dragonBoot.platform":[[11,1,1,"","DragonICE40Platform"]],"dragonBoot.platform.DragonICE40Platform":[[11,2,1,"","build"],[11,2,1,"","buildSlots"],[11,4,1,"","flash"]],"dragonBoot.platforms.audioInterface":[[10,1,1,"","AudioInterfacePlatform"]],"dragonBoot.spi":[[4,1,1,"","SPIBus"]],"dragonBoot.spi.SPIBus":[[4,2,1,"","elaborate"]],"dragonBoot.windows":[[7,1,1,"","WindowsRequestHandler"],[7,0,0,"-","descriptorSet"]],"dragonBoot.windows.WindowsRequestHandler":[[7,2,1,"","elaborate"],[7,2,1,"","handlerCondition"]],"dragonBoot.windows.descriptorSet":[[7,1,1,"","GetDescriptorSetHandler"]],"dragonBoot.windows.descriptorSet.GetDescriptorSetHandler":[[7,2,1,"","elaborate"],[7,3,1,"","elementSize"],[7,2,1,"","generateROM"]],dragonBoot:[[9,0,0,"-","bootloader"],[4,0,0,"-","spi"],[7,0,0,"-","windows"]]},objnames:{"0":["py","module","Python module"],"1":["py","class","Python class"],"2":["py","method","Python method"],"3":["py","attribute","Python attribute"],"4":["py","property","Python property"]},objtypes:{"0":"py:module","1":"py:class","2":"py:method","3":"py:attribute","4":"py:property"},terms:{"0":[1,4,5,6,7,9,11],"00":1,"0000":7,"0002":7,"01":3,"0110":1,"05":1,"0a9ba686a13223ad1faf99fc73a31441da9fa7ecaea6fd7028":1,"0kib":1,"0x00":11,"0x00000000":11,"0x00000001":11,"0x00000002":11,"0x00000004":11,"0x00000005":11,"0x00000006":11,"0x00000007":11,"0x00000008":11,"0x00000009":11,"0x001000":1,"0x01":11,"0x03":11,"0x040000":1,"0x05":11,"0x06":11,"0x08":11,"0x080000":1,"0x10":11,"0x20":11,"0xff":11,"1":[1,4,5,11],"10":[1,5],"100":1,"100m":1,"100ma":3,"103519":1,"11":[1,7],"110356":1,"110462":1,"1209":1,"132":1,"135100":1,"13mhz":10,"14":1,"16":[1,7,11],"160":1,"169157":1,"171":4,"19":1,"1a6ef18f68ac76d54f136cbb72a06cfed374e3d2ee7d4b8167":1,"1c":1,"1d88d4272e763397dcc824659a322782992c9db0":1,"2":[1,3,4,5,7,11],"20":1,"2005":1,"2009":1,"2010":1,"2021":1,"21":1,"2118ecd4645dd6b07b524d9bfa904056870ca5ed46fc88cb5359634ce4f11f54":1,"2125109630":11,"217d4ea76ad3b3bbf146980d168bc7b3b9d95a18":1,"21jaa3jl":1,"22":1,"23":1,"24":[4,5],"25":1,"28":11,"28a109e5263fd92a18efea3cec20ea1829c7baf1":1,"2d0a23b75ebb769874719297dec65ff07ca9e79f":1,"2e":1,"3":[1,3,4,5,11],"30":1,"31":1,"32":[7,11],"362be3dc234ef55609499c1b44dc5161fa604f74508d8abeb5615aa95b76cad6":1,"37":1,"38202":1,"3959cc346afc0a482f59d83cb9630bdabb16fad378dacd8341":1,"3e":1,"4":[1,5,7,11],"4096":1,"442478":1,"46":1,"4a":1,"5":[1,4,5,11],"512":1,"53":1,"54":1,"57694":1,"57f476ac1359a9d8ddbc9e2ef1a69b0d788336923ab4872a69a5081dd3e5be30":1,"5e":1,"6":[1,4,11],"60mhz":10,"61":1,"61c8ebafef421bf829914e0262782f6dd9e216803fcab823d8c6106cc61141c":1,"64":1,"6697":1,"68":1,"7":[7,11],"71":1,"72":1,"8":[1,4,7,11],"86bf051eb0ebefdedac1af65e25536176562ed531d2981cd86":1,"89":1,"8b85afa72e09b334b29c28565709cd50d8112d11":1,"8c2f90aaf7485d3c2b6b2a7fcc9254c32887628a4a10463f802eca838fe75a14":1,"9":[1,5,11],"90":1,"99":1,"9c":1,"9dec9c575f28bfb6d38bdb4562f3448ec2155a7f7b65e0fdec":1,"abstract":11,"byte":[1,4,5,7,11],"class":[3,4,5,7,9,10,11],"const":11,"default":[7,9,10,11],"do":[1,5,10,11],"enum":[5,11],"final":[1,4,11],"function":[1,3,6,11],"import":[1,8],"int":[7,11],"new":[1,5,15],"return":[1,4,5,7,9,11],"short":11,"static":11,"switch":[3,7,11],"true":11,"while":[5,7,9],A:[1,4,5,7,9,10,11],As:[5,6],For:[1,11,13],If:[1,5,7,15],In:[3,7],It:[3,5,7,9,11],NO:1,No:[1,4],Of:5,On:4,That:3,The:[1,3,5,6,7,8,10,11],Then:[1,5],There:1,To:[1,7,11,12],_buildslot:11,a3:1,a4:1,a9669acae7d8eb84834eaf68fb4fede07adf7d24bdbcb8ff00da338bd4e7653f:1,ab:1,abov:[5,7],absolut:1,access:[5,7,10],accord:7,accordingli:7,ack:[5,7],acknowledg:[4,5],act:5,action:4,activ:1,ad:1,address:[4,5,7,11],addresslength:11,adjust:1,adn:4,advanc:15,ae74f176b6ca32b24ab08325159a19318711a5a9:1,ae:1,after:[5,11],again:5,aid:[11,12,13],align:7,all:[1,3,5,7,9,11],allow:[3,5,7,10,11],along:6,alreadi:[1,3],also:[3,5,10,11],alt:4,altern:[1,3],amaranth:[1,4,5,7,9,11,12],amaranth_5cd8546b83f64ed4b1dac3c949a3c754:1,amaranth_board:1,amaranth_fc7092b8b38d4eed93ff74f26847c9ca:1,amaranth_soc:1,amaranth_stdio:1,american:3,amount:7,amranth:[5,7],an:[3,4,5,7,9,11,15],ani:[1,3,11,13],anoth:5,app_data_dir:1,appdir:1,append:11,appidl:1,applic:3,appropri:9,apt:1,ar:[1,3,5,7,9,11,13,15],arachn:1,arachne_104c527196d2447fb94b96fcda2324f1:1,arch:1,archlinux:1,area:11,arg:[4,5,7,9],ask:[3,11],assert:5,assign:3,associ:[7,10],ast:[5,7],attempt:[1,5],audio:[1,13],audiointerfac:[1,10],audiointerfaceplatform:10,aur:1,automat:[3,11],auxiliari:11,avail:1,avoid:3,await:5,back:5,badb:1,badc:1,bankheight:11,banknumb:11,bankoffset:11,bankwidth:11,bare:10,base:[8,11],bashactiv:1,bat:1,becaus:11,been:[7,11,12],befor:5,begin:[4,5,7,11],beginaddr:4,beginaddress:11,behaviour:[3,4,5,7,9],being:[3,4,5,7,11],belong:7,below:[1,4],best:3,better:1,big:11,bin:1,binari:[3,14],bind:3,bit:[5,7,11],bitsinteg:11,bitstream:[1,5,11],bitstreammag:11,bitstruct:11,blob:1,block:[1,9,11],bo:3,board:[1,10],boards_644c2f7558a043989a7dcce7d5aa821f:1,boards_9ab0a8652b924697ac0881d0d5224462:1,boilerpl:[5,11],boot:[1,11],bootaddress:11,bootload:[1,5,7,9,11,15],bootmod:11,both:[11,15],bound:5,boundari:7,box:3,bramdata:11,brew:1,bring:1,bu:[3,4,5],buffer:4,bug:1,build:[1,11],build_dir:11,builder:[1,11],buildplan:11,buildproduct:11,buildslot:11,built:1,bundl:1,busi:5,bytearrai:11,bytecount:[4,11],bytesinteg:11,c0:1,c2f5fd37f954a213ef176ba247addb8d6c966f9d:1,cach:1,cad:1,calcul:11,call:[1,11],can:[1,3,4,5,11],cannot:3,capabl:[1,11],caus:3,cbfa63d4de4a4895929567ff869e65498ab98433ca29d54e17:1,cd:1,ce0649683ee6a0839a3be8d2776b85fb1ec10dd6:1,ceff2d9438e0a515490eabb78f987bc45855a7810455a13f2ba2fb50f7be2724:1,chang:[3,5],check:[5,7,15],check_get_descriptor_set:7,chip:4,choic:14,choos:[3,14],ci:1,claim:1,clear:[1,7],cli:11,clock:[7,9,10],clone:1,code:[3,7],cold:11,coldboot:11,collect:[1,7],com:1,combinatori:[5,7],come:[5,11],command:[1,4],commit:1,commun:[1,9],complet:[1,4,5,6,7,9],complianc:3,compliant:3,compon:[1,8],compris:[4,8],conclud:7,condit:[1,5,7],configur:[1,3,5,7,9,10,11],conform:5,connect:9,consid:5,consider:1,consist:[1,7,11],constant:11,construct:[1,11],constructor:11,contain:[1,5,7,11],continu:1,control:[3,5,6,7,8],copi:1,copyright:1,core:3,correct:[7,11],correctli:5,correspond:5,corrupt:5,could:1,count:4,coupl:1,cover:11,cp310:1,cpython3:1,cpython3posix:1,cramdata:11,crccheck:11,creat:[1,5,11],creator:1,cs:4,cshellactiv:1,current:[4,5,7],custom:3,cycl:[4,7],d:[1,11],da68220833cbe4ba2ed7140c021a732401dde6791b31a664f3:1,darwin:1,data0:7,data1:7,data:[1,4,5,7,11],deal:7,debian:1,decod:5,defens:5,defin:[3,4,5,7,9,10,11,12,13],delai:3,deliv:7,depend:[1,11,14],deploi:14,deriv:5,describ:[4,5,7,9,10,11],descript:[4,5,7,9],descriptor:[5,6,7,9,11],descriptorcollect:7,descriptorset:7,design:4,dest:1,detach:[1,3,5],detail:[1,9,11],determin:[1,7],dev11:1,dev172:1,dev19:1,dev208:1,dev209:1,dev303:1,dev334:1,dev49:1,develop:13,devic:[1,3,4,5,7,8,10,11,14],dfu:[1,3,6,15],dfu_detach:3,dfuconfig:5,dfuidl:[1,5],dfurequesthandl:5,dfustat:5,dfustatu:5,dict:11,dictionari:11,directli:7,directori:1,distro:1,do_build:11,do_program:11,document:[9,13,15],doe:[7,9],doesn:1,domain:[7,9],don:[5,7],done:[1,3,4,11],down:3,download:[1,3,5],downloadbusi:5,downloadidl:5,downloadsync:5,dragonboot:[3,4,5,7,9,10,11,13,14],dragonice40platform:11,dragonmux:[1,13],draw:3,drudgeri:3,dscriptor:3,dsl:[4,5,7,9],due:1,duplic:11,dure:3,dx:1,e2:1,each:[3,7,11,12],easier:1,easiest:1,ecp5:1,edit:1,egg:1,either:[1,4,5,7,11,14],elabor:[4,5,7,9],elaborat:[9,11],elements:7,emitt:7,encod:11,encount:5,end:[1,4,5,7,11],endaddr:4,endaddress:11,endian:11,endpoint:[6,7,9],enforc:11,engin:[4,5],enough:5,enter:[4,5,7,11],entir:[5,6,11],entri:[5,7],enumer:[4,5],env:1,environ:1,ep0:[5,7],ephem:1,equal:[3,4],equival:1,eras:[3,4,5,11],eraseaddr:4,erasepages:4,error:[1,5],essentailli:5,eta:1,even:[3,9],exampl:1,exce:5,except:3,execut:1,exhaust:5,exist:1,experi:1,explain:4,express:11,extract:1,extracted_loc:1,extrem:[10,11],f370d869eeec5baae2251393f257a7ec8605b28066f4f21fe7:1,facilit:11,failur:5,fallback:3,fals:[1,11],famili:12,favourit:1,featur:1,few:[1,8,9],ff61ee2dba9dabb8e2d0ef0532ca27fd8400a5d160afa6f157b3a284f653d78a:1,field:7,fifo:[4,5],file:[1,3],filenam:1,filter:1,finish:[1,4,5],firmwar:14,first:[1,5,7,11],fishactiv:1,fix:11,flagsenum:11,flash:[1,3,5,8,10,11],flow:7,fly:10,follow:[1,3,5,7,11],form:[5,6,7],formatfield:11,found:1,fpga:[9,11,12,15],framework:[1,6],free:1,from:[1,3,4,5,6,7,9,10,11],fromappdata:1,fs:[3,9],full:7,fulli:[4,5],further:[1,3,4,5,11],futur:[1,3],g217d4ea:1,g28a109:1,g2d0a23b:1,g8b85afa:1,gae74f17:1,gate:[5,7],gatewar:[3,4,5,6,7,8,9,10,11,14],gc2f5fd3:1,gd25q40c:10,gener:[1,3,5,7,11],generaterom:[5,7],get:[1,3,5,7,15],get_descriptor_set:7,getdescriptorsethandl:7,git:1,github:1,given:[1,5,7,11],global:1,go:[4,11],good:[10,11],greedyrang:11,group:[5,7],guid:15,ha:[1,5,7,11],hand:3,handl:[5,6,7,9],handle_detach:5,handle_download:5,handle_download_complet:5,handle_download_data:5,handler:[3,8,9],handlercondit:[5,7],handshak:7,harald:1,hardwar:1,have:[1,3,5,10,11,12],hdl:[4,5,7,9],headphoneamp:[1,13],heavi:1,held:7,helper:[1,13],high:9,highest:7,hold:7,home:1,homebrew:1,host:[3,4,5,7,9],hous:9,how:[5,11,14],howev:[1,5,9],hs:[3,10],http:1,hurt:5,ice40:[1,12],ice40up5k:9,icestorm:[10,11],id:[1,7],identifi:[4,5],idl:[4,5,7],ie:5,imag:[1,5,11],immun:3,implement:[3,5,7,9,11,12,13],implment:3,imposs:5,inc:1,includ:11,incom:[4,5,7],index:7,indic:[4,5,7],industri:1,inf:3,inform:[5,7],init:1,initi:[1,11],initialis:4,inner:11,inout:7,input:[4,7],instanc:[7,9],instead:[7,9],instruct:[1,4,11,13],integ:11,interest:5,interfac:[1,3,5,7,9,13],intern:4,internaloscrang:11,invalid:1,invert:4,invok:1,ir:9,issu:1,its:[4,5,10,11],itself:4,jinja2:1,just:[3,5,15],kb:1,keep:[3,7],kind:5,know:5,kwarg:[4,5,7,9,11],laid:[5,7],lambdasoc:1,lang:1,largest:7,last:4,latest:1,latter:7,lattic:[1,9,11],layout:[5,11],least:5,length:[5,7],less:5,let:5,level:9,lib:1,line:1,linux:1,list:[7,11],load:4,local:1,locat:11,logic:[3,9,11],look:14,ls:9,luna:[1,3,5,6,7,8],luna_d8cb58b30cf84ad5a38f6517eeb86922:1,machin:[5,7],maco:1,mai:3,maiden:1,main:[1,5,7,11],major:4,makepkg:1,manag:1,manifest:3,manner:7,manual:3,manylinux1_x86_64:1,manylinux2014_x86_64:1,manylinux_2_17_x86_64:1,markupsaf:1,match:5,matter:3,max:[3,11],maximum:7,maxpacketlength:7,maxpackets:7,mb:1,mean:[3,7],meet:11,mem:[5,7],memori:[5,7],metadata:1,microcontrol:15,microsoft:7,minimum:[1,3,10],mode:[1,3,4,9,11],modul:[1,4,5,7,9],mon:1,most:[5,7],msys2:1,multi:[1,11],multipl:4,must:[1,5,11],name:[1,11],need:[1,3,4,5,7,9,13],net:1,newer:[1,3],next:[1,4,7,11],nightli:1,no_vcs_ignor:1,non:[4,5],none:[1,4,11],normal:11,notabl:5,note:[3,4,5,7],number:[3,4,5,7,11,13],nushellactiv:1,object:[3,5,7,10,11],off:3,offset:[7,11],ok:5,old:1,older:[1,3],onc:[1,5,7,11],one:[1,3,5],ones:3,onli:[1,5,7,11],opcod:[4,11],open:1,openmoko:1,oper:[4,5,7,9,10,11],option:11,order:[5,11],org:1,os:7,oss:1,ostens:9,other:[1,3,5,9,11],otherwis:[10,11],our:[3,7,10],out:[3,4,5,7,10,11,15],output:[4,5,7],overarch:4,p:1,packag:1,packet:[5,7],pacman:1,pad:[7,11],page:[1,3,4,5,11],pageprogram:4,pair:11,paramet:[4,5,7,9,10,11],part:[1,3,4,5,7],particular:[3,5],partit:[5,11],pass:[4,5,11],path:1,payload:[5,11],pc:1,pend:4,per:[3,11],perform:[5,10,11],perman:1,phase:[5,7],phy:10,physic:3,pick:1,pid:1,pip3:1,pip:1,place:[1,11],placement:[10,11],platform:[1,3,4,5,6,8,9],platformdescriptorcollect:7,pleas:[1,15],por:11,portion:6,posit:7,possibl:[3,9],post31:1,power:3,powershellactiv:1,prefer:1,preinstal:1,prepar:1,presenc:11,present:1,primari:1,print:5,printslotinfo:5,prior:4,process:5,produc:10,program:[1,11],program_opt:11,progress:4,project:15,proper:11,properti:11,protocol:[1,3,4,5],protocol_35a396f403f9431aaa48963803a3a511:1,protocol_7c85d4eaaaff4e61beb52a6fa8eed1e2:1,provid:[9,10],pull:5,puls:7,push:5,py2:1,py3:1,py:[1,5],pyproject:1,pyseri:1,python3:1,python:3,pythonactiv:1,pyvcd:1,q:1,qk963uua:1,qualifi:[4,5],quiet:1,r:1,r_data:4,raw:[9,11],re:5,react:[5,7],read:[4,11],readaddr:4,readi:[4,5],readstatu:4,realli:1,reason:[10,11],reattach:1,reboot:[5,9,11],rebuild:11,rebuilt:11,receiv:3,recent:[5,7],recomend:1,reconfigur:[9,11],recurs:1,reduc:11,regardless:14,regist:5,releas:1,releasepowerdown:4,repeat:3,repo:1,report:[1,5],request:[1,3,4,8,9,11],requir:[3,4,5,7,9,10,11],requri:[5,10],reserv:11,reset:[4,5],resetaddr:4,resetcrc:11,resolv:1,resourc:[4,5,10,13],resovl:1,respect:[3,7],respond:[5,7,9],respons:[5,7,10],rest:[1,5,7],result:[5,14],retriev:[7,11],revis:1,rewrit:4,right:4,rom:[5,7],room:11,rout:[1,10,11,14],rule:3,run:[1,7,11],runtim:11,s:[1,3,5,7,10,11],same:11,satisfi:1,schmidt:1,secondari:5,section:[1,9,13],sector:[4,5,11],see:[4,11],seed:1,seeder:1,seen:[5,7],select:4,self:11,send:[1,5],seper:3,sequenc:4,serialis:1,set:[3,4,7,9,11],set_alternate_enum:7,setup:[1,3,5,7],setuppacket:[5,7],setuptool:1,sha256:1,share:1,should:[5,7,10,11],shrine:1,sic:1,sign:11,signal:[4,5,7],signatur:1,simpl:[1,3],simpleboot:11,singl:3,sit:11,site:1,size:[1,3,5,7,11],slot:[1,3,4,5],so:[1,3,4,5,11],soc:1,soc_832c57e5eee64c96affa5d2f2a556817:1,soc_be060f48ee744611ba50b88833e38e56:1,softwar:1,solut:3,some:[1,5,9],sourc:10,sourceforg:1,spec:[3,7],special:[11,12,13],specialopcod:11,specif:[1,3,4,5,6,9,11],specifi:7,speed:9,spi:[5,8,10],spibu:4,spiflash:4,spiflashcmd:4,spiflashop:4,spiflashprogramm:11,sport:3,src_loc_at:[4,5,7,9],stall:[5,7],standard:[3,5,6],start:[1,4,5,7,11,15],startposit:7,state:[1,5,7],statu:[1,5,7],stdio:1,stdio_f3eff8333bfc499a9ba0832c12a4b11:1,stefan:1,step:[1,5],stick:1,still:5,storag:3,store:[1,5],str:11,stream:[5,7],strictli:3,string:[3,7],strobe:[4,7],struct:11,structur:11,subclass:3,subdirectori:1,submodul:1,substitut:1,success:5,successfulli:1,sudo:1,suffici:11,suffix:1,suit:1,suitabl:[1,14],sum:[5,7],support:[3,7,12,13],swap:[7,10],sy:3,synthesi:[10,11],synthesis:[4,5,7,9],system:[4,5,7],t:[1,5,7],talk:[4,9],tarbal:1,target:[1,3,7,11,13,14],task:10,technic:5,tell:[5,9],termin:1,than:[1,5],thei:[5,7],therefor:5,thi:[1,3,4,5,6,7,9,10,11,13,15],thing:[7,9],those:13,three:6,through:[4,5,6,11],ticket:1,till:[5,11],time:1,timeout:3,tjjqkdfm:1,tmp:1,togeth:11,toml:1,too:1,tool:[1,3,11],toolchain:[1,10,11],toolchain_program:11,top:[9,11],tormod:1,track:[5,7],transfer:[1,3,4],transit:5,transmit:7,tri:5,trigger:[5,7],triggerreboot:5,tupl:7,two:[1,4,11],tx:7,txt:1,type:[4,5,7,9,11,12],ubuntu:1,ulpi:9,unabl:9,unavail:1,unconfigur:11,under:[5,7],underli:[4,11],uninstal:1,union:11,uniqu:3,unless:[10,11],unset:11,unsign:11,until:[4,11],up:[3,4,9],updat:[1,7],upgrad:[1,10,11],upli:10,upload:[3,5],uploadidl:5,us:[3,4,5,6,7,9,10,11,13],usb2:9,usb3318:10,usb:[1,5,6,7,8,10,15],usb_protocol:[1,7],usbdevic:9,usbinstreaminterfac:7,user:[1,11],usual:4,util:1,valid:[1,7,11],valu:[4,5,7,11],variabl:[4,5,7],variou:3,vendor:7,version:1,via:[1,10,11],viabl:3,vid:1,virtual:1,virtualenv:1,volden:1,w_data:4,wa:5,wai:[1,3,11],wait:5,wake:3,wakeup:[3,11],want:14,warmboot:[4,9,11],warn:1,warranti:1,wasmtim:1,we:[1,3,5,7,9,11],well:5,welt:1,weston:1,what:9,wheel:1,when:[1,3,4,5,7,11],where:[1,3,4,5,11],which:[3,4,5,7,9,10,11],whl:1,window:[1,3,6],windowsrequesthandl:[3,7],winusb:3,wish:1,work:[3,7,9,11],would:5,write:[1,4,11],writeaddr:4,writeen:4,written:[4,5,11],wsl2:1,x64:1,x:3,xfer:4,yet:7,you:[1,10,11,14,15],your:[1,11,13,14],yowasp_nextpnr_ecp5:1,yowasp_nextpnr_ice40:1,yowasp_yosi:1,ytg_6dcc:1,zero:[1,5],zlp:5},titles:["Deploying the firmware","Deploying the gateware","dragonBoot for microcontroller","USB Descriptors","The SPI Flash controller","DFU Request Handler","Request Handlers","Windows Platform-Specific Request Handler","dragonBoot for FPGA","The LUNA-based USB Device","dragonmux/HeadphoneAmp audio interface platform","iCE40 Platform Helper","Platform Helpers","Platforms","Getting Started","dragonBoot"],titleterms:{The:[4,9],audio:10,base:9,control:4,deploi:[0,1],descriptor:3,devic:9,dfu:5,dragonboot:[1,2,8,15],dragonmux:10,firmwar:0,flash:4,fpga:8,gatewar:1,get:14,handler:[5,6,7],headphoneamp:10,helper:[11,12],ice40:11,instal:1,interfac:10,luna:9,microcontrol:2,nativ:1,nextpnr:1,platform:[7,10,11,12,13],python:1,request:[5,6,7],requir:1,set:1,slot:11,specif:7,spi:4,start:14,system:[1,11],todo:1,up:1,us:1,usb:[3,9],window:7,yosi:1,yowasp:1}})