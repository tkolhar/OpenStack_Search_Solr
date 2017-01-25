# OpenStack_Search_Solr

                                                                                            
Data is a valuable resource. Unstructured data has been growing
enormously.

Although we have facilities to handle and store the data using swift, amazon S3.

The basic implementation of Search is missing. 

This really blocks other peripheral usecases such as content search, de-duplication. 

At a stage where we are dealing with minimizing our storage cost and improve efficiency, these
functionalities even though basic provide a great contribution to existing feature.

The main objective of this research is enhancing the current openstack swift architecture by clubbing it with 
some search engine SOLR to be precise. 

There are 2 algorithms implemented in python. 

First is introduction of content searchfeature and Second is algorithm to prevent de-duplication of 
data. 

This plugin allows us to extract the data without the overhead of downloading the data. This plays a biggest concern when one is dealing with large scale heterogenous unstructured data coming from multiple sources.


	INSTALLATION STEPS AND SETTING UP THE VIRTUAL MACHINES

	VIRTUAL MACHINE SETUP:

Install Vmware Workstation Player:

http://www.vmware.com/products/player/playerpro-evaluation.html

Create Virtual Machine:

Provide Centos ISO while creating the Virtual machine.

The other parameters would be RAM, No of Processors

	HARDWARE – 4GB RAM MINIMUM, PROCESSOR WITH HARDWARE

	VIRTUALIZATION EXTENSIONS

For network We are using Bridging of Network so that the copy of our host network
is adopted by our Virtual machine network

Also, we assign static ip address to the machine
for my system I setup :

    vim /etc/sysconfig/network-scripts/ifcfg-eno-16777736

    TYPE=Ethernet

    BOOTPROTO=static

    DEFROUTE=yes

    IPV4_FAILURE_FATAL=no

    IPV6INIT=yes

    IPV6_AUTOCONF=yes

    IPV6_DEFROUTE=yes

    IPV6_FAILURE_FATAL=no

    NAME=eno16777736

    UUID=4711a184-5a95-4861-b3e1-5626bb3f8234

    DEVICE=eno16777736

    ONBOOT=yes

    PEERDNS=yes

    PEERROUTES=yes

    IPV6_PEERDNS=yes

    IPV6_PEERROUTES=yes

    IPADDR=192.168.0.28

    NETMASK=255.255.255.0

    $service network restart

    $chkconfig network on

    $service NetworkManager stop

    $chkconfig NetworkManager off

    	OPENSTACK INSTALLATION AND SETUP:

    	NETWORK –
    o	$ sudo systemctl disable firewalld

    o	$ sudo systemctl stop firewalld

    o	$ sudo systemctl disable NetworkManager

    o	$ sudo systemctl stop NetworkManager

    o	$ sudo systemctl enable network

    o	$ sudo systemctl start network

    	INSTALLATION:
    •	sudo yum install -y centos-release-openstack-newton

    •	sudo yum update -y

    •	sudo yum install -y openstack-packstack

    •	sudo packstack –allinone

    	Once, the setup is complete, a file is created :

    $ cat keystonerc_admin 

    unset OS_SERVICE_TOKEN

    export OS_USERNAME=admin
    
    export OS_PASSWORD=ea12f4366a2a4253
    
    export OS_AUTH_URL=http://192.168.0.28:5000/v2.0
    
    export PS1='[\u@\h \W(keystone_admin)]\$ '
    
    export OS_TENANT_NAME=admin

    export OS_REGION_NAME=RegionOne

These are the environment variables which we use in our code

The dashboard in my case will be accessed here 

http://192.168.0.28/dashboard.

	SOLR INSTALLATION STEPS:

•	CHECK JAVA INSTALLED :

•	java -version

•	java version "1.8.0_60"

•	Java(TM) SE Runtime Environment (build 1.8.0_60-b27)

•	Java HotSpot(TM) 64-Bit Server VM (build 25.60-b23, mixed mode)


	Solr is available from the Solr website at http://lucene.apache.org/solr/.
http://www.apache.org/dyn/closer.lua/lucene/solr/6.3.0

•	EXTRACT THE TAR FILE
cd ~/

tar zxf solr-x.y.z.tgz

•	START SOLR

    bin/solr start

IF WINDOWS then

    bin\solr.cmd start

•	TO CHANGE THE PORT ON WHICH IT IS RUNNING

    bin/solr start -e techproducts -p 8984

•	STOP SOLR

    bin/solr stop -e techproducts -p 8983

     bin/solr stop 

•	THIS IS HOW SOLR INDEXES THE DOCUMENTS

    [tazimk@localhost exampledocs]$/opt/solr/bin/post -c techproducts   /opt/solr/example/exampledocs/Test.pdf -params literal.id=3
    java -classpath /opt/solr/dist/solr-core-5.4.0.jar -Dauto=yes -Dparams=literal.id=3 -Dc=techproducts -Ddata=files org.apache.solr.util.SimplePostTool /opt/solr/example/exampledocs/Test.pdf

    SimplePostTool version 5.0.0

    Posting files to [base] url http://localhost:8983/solr/techproducts/update?literal.id=3...

     Entering auto mode. File endings considered are xml,json,csv,pdf,doc,docx,ppt,pptx,xls,xlsx,odt,odp,ods,ott,otp,ots,rtf,htm,html,txt,log

    POSTing file Test.pdf (application/pdf) to [base]/extract

    1 files indexed.

    COMMITting Solr index changes to http://localhost:8983/solr/techproducts/update?literal.id=3...

    Time spent: 0:00:02.762

	SEARCHING THE FILE IN SOLR WITH ITS CONTENT

In Order to Obtain Result for the indexed file One can use Curl and get data in JSON format

    [tazimk@localhost exampledocs]$ curl -XGET "http://localhost:8983/solr/techproducts/select?q=Test.pdf&wt=json"
    {"responseHeader":{"status":0,"QTime":19,"params":{"q":"Test.pdf","wt":"json"}},"response":{"numFound":1,"start":0,"docs":[{"id":"3","resourcename":"/opt/solr/example/exampledocs/Test.pdf","content_type":["application/pdf"],"content":[" \n \n  \n  \n  \n  \n  \n  \n  \n  \n  \n  \n  \n  \n  \n  \n  \n  \n  \n \n    \n Hello World \n \n   \n  \n \n  "],"_version_":1551305347674669056}]}}


        
	The results are contained in an JSON Format.

	The document contains two parts. The first part is the responseHeader, which contains information about the response itself. 

	The main part of the reply is in the response dictionary, which contains docs dictionary, each of which contains fields from documents that can match the query. 

	Using standard Python Dictionaries transformation techniques to mold Solr's JSON results into a form that is suitable for displaying to SWIFT USERS.


	Step to run the Application
Export Environment Variables for Openstack swift   

    $export OS_USERNAME=admin

    $export OS_PASSWORD=ea12f4366a2a4253

    $export OS_AUTH_URL=http://192.168.0.28:5000/v2.0
 
    $export OS_TENANT_NAME=admin
 
    $export OS_REGION_NAME=RegionOne

Run the Solr on 8983:

    $./solr start -e techproducts

Install python-docx to extract *.docx content or Word document content

    $tar xvzf python-docx-{version}.tar.gz

    $cd python-docx-{version}

    $python setup.py install

    $pip install python-docx

	https://python-docx.readthedocs.io/en/latest/user/install.html

Download it from here:

	https://pypi.python.org/pypi/python-docx

Install slate to extract pdf files data:

    $unzip slate-master.zip

There you will locate setup.py file

     $python setup.py install

Download it from here:
	https://github.com/timClicks/slate

Run the program:
$python $FILE_NAME.py



