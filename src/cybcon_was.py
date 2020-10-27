################################################################################
# cybcon_was - Cybcon Industries simple python/jython WebSphere functions library
# description: the cybcon_was library is written to give you an easy way to
#   build own WebSphere administration scripts.
# Author: Michael Oberdorf
# Date: 2009-06-30
# (C) Copyright by Cybcon Industries 2009
# Library can be downloaded at: http://www.cybcon-industries.de/
# SourceForge project page: http://sourceforge.net/projects/was-configcrawler/
#-------------------------------------------------------------------------------
# COPYRIGHT AND LICENSE
#
# (C) Copyright 2009-2014, Cybcon Industries, Michael Oberdorf <cybcon@gmx.net>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#---------------------------------------------------------------------
#  $Revision: 61 $
#  $LastChangedDate: 2016-02-25 19:25:39 +0100 (Thu, 25 Feb 2016) $
#  $LastChangedBy: cybcon89 $
#  $Id: cybcon_was.py 61 2016-02-25 18:25:39Z cybcon89 $
################################################################################

#----------------------------------------------------------------------------
# Definition of global variables
#----------------------------------------------------------------------------

cybcon_was_lib_version="1.033";                       # version of this library

# import standard modules
import time;                                          # module for date and time
import sys;                                           # system libraries
import java.lang.System;                              # java system library

# try to import WebSphere specific libraries (see POD for details)
try:
  import AdminConfig;
  import AdminControl;
  import AdminApp;
  import AdminTask;
  import Help;
except:
  pass;

# set the line separator variable
lineSeparator = java.lang.System.getProperty('line.separator'); # define line separator

#############################################################################
# simple libraries for textprocessing
#############################################################################

#----------------------------------------------------------------------------
# version
#   description: function to print out the library version
#   input: -
#   return: -
#   output: library version
#----------------------------------------------------------------------------
def version():
  print cybcon_was_lib_version;

#----------------------------------------------------------------------------
# help
#   description: function to print out the library documentation
#   input: -
#   return: -
#   output: library documentation
#----------------------------------------------------------------------------
def help():
  print "Library version: " + cybcon_was_lib_version + "\n\n";
  print documentation;

#----------------------------------------------------------------------------
# find_valueInArray
#   description: searching an value in an array
#   input: value (string), array (array of strings)
#   return: "true" | "false"
#----------------------------------------------------------------------------
def find_valueInArray(value, array):
  # return "false" if value or array is not given to function
  if value == "": return "false";
  if array == "": return "false";

  # check if value is in array
  if value in array: return "true";
  else: return "false";

#----------------------------------------------------------------------------
# get_AttributesFromObject
#   description: get an array of all attributes of an object
#   input: objectID
#   return: array of attributes
#----------------------------------------------------------------------------
def get_AttributesFromObject(objectID):
  # return "" if object ID is not given to function
  if objectID == "": return "";

  # define array to hold the attributes
  Attributes = [];

  # get all elements in the object
  for elements in AdminConfig.show(objectID).split(lineSeparator):
    if elements != "":
      # split attribute and values and get the left side (attribute)
      attribute = elements.split(" ")[0].replace("[", "");
      # if attribute not empty, append the attribute to the array
      if attribute != "":
        Attributes.append(attribute);

  # get array back
  return Attributes;

#----------------------------------------------------------------------------
# showAttribute
#   description: returns the value of an attribute from an object
#   input: objectID, attribute
#   return: value as string | ""
#----------------------------------------------------------------------------
def showAttribute(objectID, attribute):
  # return nothing if objectID or attribute name is not given to function
  if objectID == "": return "";
  if attribute == "": return "";

  # get all attributes in the object and check if the given attribute is
  # part of the objects attributes
  if find_valueInArray(attribute, get_AttributesFromObject(objectID)) == "true":
    # sleeping time to prevent exception: java.net.BindException: Address already in use: connect (WASX7017E)
    time.sleep(0.02);
    # OK, attribute exist, we can request it's value and give that value back
    return AdminConfig.showAttribute(objectID, attribute);
  else:
    # return an empty string if the attribute not exist in the object
    return "";

#----------------------------------------------------------------------------
# splitArray
#   description: takes a string and split string into an array
#   input: string
#   return: array
#----------------------------------------------------------------------------
def splitArray(string):
  # return if string is not given to function
  if string == "": return "";

  # defining array
  array = [];

  # remove leading '[' and tailing ']'
  string = string.replace("[", "").replace("]", "");

  # flag to identify if we are in parenthesis
  Parenthesis="false";

  # array value (concatenation)
  value="";

  # loop over string
  for token in string:
    if token == '"':
      # inner parantheses starts - set flag
      if Parenthesis == "false":
        Parenthesis = "true";
        continue;
      # inner paranthese end - save value
      elif Parenthesis == "true":
        Parenthesis = "false";
        if value != "": array.append(value);
        value="";
        continue;
    elif token == ' ':
      # not in parantheses - split here
      if Parenthesis == "false":
        if value != "": array.append(value);
        value="";
        continue;
      # not in parantheses - concatenate
      if Parenthesis == "true":
        value = value + token;
        continue;
    else:
      value = value + token;
      continue;

  # append last element
  if value != "": array.append(value);

  # return array
  return array;

#----------------------------------------------------------------------------
# get_ObjectTypeByID
#   description: extract the object type from the given object ID
#   input: objectID
#   return: objectType
#----------------------------------------------------------------------------
def get_ObjectTypeByID(objectID):
  # check if the objectID is given to function, return nothing if it is not
  if objectID == "": return "";

  # cut the objectID string to it's components
  # cut the string at the first '#' - take the right side of the string
  objectType = objectID.split("#")[-1];
  # cut the string at the first '_' - take the left side of the string
  objectType = objectType.split("_")[0];
  
  # give objectType back
  return objectType;

#----------------------------------------------------------------------------
# get_ObjectScopeByID
#   description: try to identify the object scope from the given object ID
#   input: objectID
#   return: objectScope ("Server" | "ServerCluster" | "Node" | "Cell")
#----------------------------------------------------------------------------
def get_ObjectScopeByID(objectID):
  # check if the objectID is given to function, return nothing if it is not
  if objectID == "": return "";

  # cut the objectID string to it's components
  # cut the string at the first '|' - take the left side of the string
  objectScope = objectID.split("|")[0];
  # cut the string at the first '(' - take the right side of the string
  objectScope = objectScope.split("(")[-1];
  # check for the scope and give scope back
  if objectScope.find("/clusters/") != -1: return "ServerCluster";
  if objectScope.find("/servers/") != -1: return "Server";
  if objectScope.find("/nodes/") != -1: return "Node";
  return "Cell";

#----------------------------------------------------------------------------
# get_nodeNameByServerID
#   description: get the serverID and return the nodeNAme on which the server
#     is scoped
#   input: serverID
#   return: nodeName | NULL
#----------------------------------------------------------------------------
def get_nodeNameByServerID(serverID):
  # check if serverID is given to function, return nothing it it is not
  if serverID == "": return "";

  # get cellName
  cellName = AdminControl.getCell();
  # get serverName
  serverName = showAttribute(serverID, 'name');
  # loop over nodes
  for nodeName in get_nodeNames():
    # try to get the serverID on the node
    serverIDperNode = AdminConfig.getid('/Cell:' + cellName + '/Node:' + nodeName + '/Server:' + serverName + '/');
    # return if the generated serverID is the same as the given serverID
    if serverIDperNode == serverID: return nodeName;

  # return NULL
  return "";

#----------------------------------------------------------------------------
# parse_mbean
#   description: parses a MBean and store it's single parameters to a
#     hash table
#   input: mbean
#   return: dictionary
#----------------------------------------------------------------------------
def parse_mbean(mbean):
  # return if mbean is not given to function
  if mbean == "": return;

  # defining new hashtable (dictionary)
  MB = {};
  # defining temporarily array
  tmp_params = [];

  # split the MBean string in the main parts  "WebSphere:" mbean_params "#" mbean_reference
  [ mbean_params, mbean_reference ] = mbean.split("#");
  mbean_params = mbean_params.split(":")[1];

  # store the single parameters to the hashtable
  tmp_params = mbean_params.split(",");
  for tmp_param in tmp_params:
    [tmp_att, tmp_val ] = tmp_param.split("=");
    MB[tmp_att] = tmp_val;

  # give hashtable back
  return MB;

#############################################################################
# functions to get informations about the websphere infrastructure
#############################################################################

#----------------------------------------------------------------------------
# get_nodeNames
#   description: get the node names from the cell
#   input: -
#   return: array of node names
#----------------------------------------------------------------------------
def get_nodeNames():
  # define array
  Nodes = [];

  # loop over nodes
  for myNode in AdminTask.listNodes().split(lineSeparator):
    # append node name if it is not empty
    if myNode != "": Nodes.append(myNode);

  # return the array of node names
  return Nodes;

#----------------------------------------------------------------------------
# get_nodeAgentID
#   description: get the object ID of the node agent per node
#   input: nodeName
#   return: node agent ID
#----------------------------------------------------------------------------
def get_nodeAgentID(nodeName):
  # return if nodeName is not given to function
  if nodeName == "": return;

  # define array
  NodeAgents = [];

  # get cell
  cellName = AdminControl.getCell();
  cellID = AdminConfig.getid('/Cell:' + cellName + '/');

  # get the Nodeagents
  for nodeAgentID in AdminConfig.list('NodeAgent', cellID).split(lineSeparator):
    # separate node name from the node agent IDs
    nodeNameOfAgent = nodeAgentID.split("(")[1];
    nodeNameOfAgent = nodeNameOfAgent.split("|")[0];
    nodeNameOfAgent = nodeNameOfAgent.split("/")[3];

    # if the node name in the node agent id is the same as the given node name
    # give the agent ID back
    if nodeNameOfAgent == nodeName: return nodeAgentID;

  # return nothing if no nodeagent is found
  return "";

#----------------------------------------------------------------------------
# get_clusterNames
#   description: get all cluster names
#   input: -
#   return: array of cluster names
#----------------------------------------------------------------------------
def get_clusterNames():
  # define array
  Clusters = [];

  # loop over Clusters
  for myCluster in AdminConfig.list("ServerCluster").split(lineSeparator):
    if myCluster == "":
      continue;
    myClusterName = showAttribute(myCluster, 'name');
    if myClusterName != "":
      Clusters.append(myClusterName);

  # return the array of node names
  return Clusters;

#----------------------------------------------------------------------------
# get_clusterMemberNames
#   description: get all names of the cluster members
#   input: clusterName
#   return: array of cluster member names
#----------------------------------------------------------------------------
def get_clusterMemberNames(clusterName):
  # return if cluster name is not given to function
  if clusterName == "": return;

  # define array for the cluster member names
  clusterMemberNames = [];

  # get the ID from the cluster name
  clusterID = AdminConfig.getid('/ServerCluster:' + clusterName + '/');

  # get the cluster member IDs from the cluster
  for clusterMemberID in showAttribute(clusterID, 'members').replace("[", "").replace("]", "").split():
    # get the name of the cluster member
    serverName = showAttribute(clusterMemberID, 'memberName');

    # append name to array if the name is not empty
    if serverName != "": clusterMemberNames.append(serverName);

  # return array
  return clusterMemberNames;

#----------------------------------------------------------------------------
# get_serverMembersByNodeName
#   description: get the names from all server members by node
#   input: name of node
#   return: array of names
#----------------------------------------------------------------------------
def get_serverMembersByNodeName(nodeName):
  # return if node name is not given to function
  if nodeName == "": return;

  # make node name to lower case
  nodeName = nodeName.lower();

  # define array
  servers = [];

  # loop over all servers
  areThereChanges=AdminConfig.hasChanges();
  for myServer in AdminConfig.list("Server").split(lineSeparator):
    # check if the server is on the given node
    if myServer.lower().find(nodeName) != -1:
      # get the name from the server object
      serverName = showAttribute(myServer, 'name');
      # append server name if it is not empty
      if serverName != "": servers.append(serverName);

  # The AdminConfig.list("Server") will do something in the cache a modification
  # when a webserver is in the list. This will not happen regulary. But to prevent
  # the WARNING message: "WASX7309W: No "save" was performed ...", I will clean up
  # that "change"
  if AdminConfig.hasChanges() == 1 and areThereChanges == 0: AdminConfig.reset();

  # return the array of server member names
  return servers;

#----------------------------------------------------------------------------
# get_applications
#   description: get a list of all installed applications
#   input: -
#   return: array of application names
#----------------------------------------------------------------------------
def get_applications():
  # define array in which the application names will be append
  applications = [];

  # get the list of names of installed applications
  for appName in AdminApp.list().split(lineSeparator):
    # push application name to array if it is not empty
    if appName != "": applications.append(appName);

  # return the array
  return applications;

#----------------------------------------------------------------------------
# identify_serverOrClusterByName
#   description: identify the object type (Server or ServerCluster) by
#     searching the name in the list of clusters and/or servers.
#     at first, searching in the cluster list, first match was send back
#     return empty string if name is not found in the lists
#   input: objectName
#   return: "ServerCluster" | "Server"
#----------------------------------------------------------------------------
def identify_serverOrClusterByName(objectName):
  # return if node name is not given to function
  if objectName == "": return "";

  # define arrays
  clusterlist = [];
  serverlist = [];

  # get all configured clusters
  for myCluster in AdminConfig.list("ServerCluster").split(lineSeparator):
    # if the cluster ID is not empty
    if myCluster != "":
      # get the cluster name
      clusterName = showAttribute(myCluster, 'name');
      # append cluster name to array if it is not empty
      if clusterName != "": clusterlist.append(clusterName);

  # check if the given name is in the cluster list
  if find_valueInArray(objectName, clusterlist) == "true": return "ServerCluster";

  # ok, at this point we know it is no cluster, proceed with the serverlist
  # get all configured servers
  areThereChanges=AdminConfig.hasChanges();
  for myServer in AdminConfig.list("Server").split(lineSeparator):
    # if the server ID is not empty
    if myServer != "":
      # get the server name
      serverName = showAttribute(myServer, 'name');
      # append server name to array if it is not empty
      if serverName != "": serverlist.append(serverName);

  # The AdminConfig.list("Server") will do something in the cache a modification
  # when a webserver is in the list. This will not happen regulary. But to prevent
  # the WARNING message: "WASX7309W: No "save" was performed ...", I will clean up
  # that "change"
  if AdminConfig.hasChanges() == 1 and areThereChanges == 0: AdminConfig.reset();

  # check if the given name is in the server list
  if find_valueInArray(objectName, serverlist) == "true": return "Server"

  # ok, at this point we know it is also no server
  return "";

#----------------------------------------------------------------------------
# get_applicationStateOnServer
#   description: get the state of an application on a single server member
#   input: string (application name), string (server name)
#   return: string (status): "started" | "stopped"
#----------------------------------------------------------------------------
def get_applicationStateOnServer(appName, serverName):
  # return "stopped" if application name or server name is not given to function
  if appName == "": return "stopped";
  if serverName == "": return "stopped";

  # look if the MBean of the application exists - if it exists, the application is running
  if AdminControl.queryNames('type=Application,name=' + appName + ',process=' + serverName + ',*') != "":
    return "started";
  else:
    return "stopped";

#----------------------------------------------------------------------------
# get_applicationIDByName
#   description: get the objectID of an application by it's application name
#   input: string (application name)
#   return: objectID | ""
#----------------------------------------------------------------------------
def get_applicationIDByName(appName):
  # return empty string if application name is not given to function
  if appName == "": return "";

  # get application deployment
  deployments = AdminConfig.getid('/Deployment:' + appName + '/');
  if deployments == "": return "";

  # get the application object off the deployment
  deploymentObject = showAttribute(deployments, 'deployedObject');
  if deploymentObject == "": return "";
  else: return deploymentObject;

#----------------------------------------------------------------------------
# get_applicationTargetServerNames
#   description: get the server names on which the application is configured
#   input: string (application name)
#   return: array of server names
#----------------------------------------------------------------------------
def get_applicationTargetServerNames(appName):
  # return empty string if application name is not given to function
  if appName == "": return "";

  # defining array to store server names
  serverNames = [];

  # get objectID of the application
  appID = get_applicationIDByName(appName);

  # get all targets on which the application is mapped
  for targetMappingID in splitArray(showAttribute(appID, 'targetMappings')):
    # continue if no mapping exists
    if targetMappingID == "": continue;

    # get the name of the target
    targetID = showAttribute(targetMappingID, 'target');
    targetName = showAttribute(targetID, 'name');

    # identify the target by it's name
    targetType = identify_serverOrClusterByName(targetName);

    # target is a cluster, get server members in cluster
    if targetType == "ServerCluster":
      # loop over cluster members
      for serverName in get_clusterMemberNames(targetName):
        # append serverName if it is not already in array
        if find_valueInArray(serverName, serverNames): serverNames.append(serverName);

    # target is a server
    if targetType == "Server":
      if find_valueInArray(targetName, serverNames): serverNames.append(targetName);

  # get serverlist back
  return serverNames;

#----------------------------------------------------------------------------
# get_applicationState
#   description: get the state of an application
#   input: string (application name)
#   return: string (status): "started" | "stopped" | "partially" | "unmapped"
#----------------------------------------------------------------------------
def get_applicationState(appName):
  # return "stopped" if application name is not given to function
  if appName == "": return "stopped";

  # defining variables
  FLAG_true = "unset";
  FLAG_false = "unset";

  # get target server members from application name
  serverNames = get_applicationTargetServerNames(appName);

  # loop over server name and set the FLAGs
  for serverName in serverNames:
    if get_applicationStateOnServer(appName, serverName) == "started": FLAG_true = "set";
    else: FLAG_false = "set";

  # check the flags and return values
  # FLAG_true -> application is started
  # FLAG_false -> application is stopped
  if FLAG_true == "set" and FLAG_false == "set": return "partially";
  if FLAG_true == "unset" and FLAG_false == "set": return "stopped";
  if FLAG_true == "set" and FLAG_false == "unset": return "started";
  if FLAG_true == "unset" and FLAG_false == "unset": return "unmapped";

#----------------------------------------------------------------------------
# parse_adminAppView
#   description: parse the output of AdminApp.view(appName, option) and
#     return an array of disctionaries
#   input:
#     string (application name)
#     string (option from AdminApp.options(application name)),
#     string (startKey that identifies the start of the information part)
#   output: -
#   return: array of dictionaries | null
#----------------------------------------------------------------------------
def parse_adminAppView(appName, option, identifier):

  # make option lower case
  option=option.lower();

  # define the master array that hold the information
  AppInf=[];

  # starting flag that inidicates the start if given identifier matches
  startFlag='false';

  # loop over all valid options for the application, if given option
  # was found, proceed with detailed view
  for validOption in AdminApp.options(appName).split(lineSeparator):
    # check if the option is valid for application
    if validOption.lower() == option:
      # option found, start parsing option details
      for line in AdminApp.view(appName, '-' + validOption).split(lineSeparator):
        line = line.strip();
        if line == '': continue;    # skip empty lines
        if startFlag == 'false':
          if line.find(identifier) != -1:
            startFlag='true';                 # first entry found
            AppInf.append({});                # initialize dictionary
            AppInfIndex=len(AppInf) - 1;      # get index of array
            att, val = line.split(":",1);     # split the line in attribute and value pair
            att=att.strip();                  # remove leading and trailing whitespaces from attribute
            val=val.strip();                  # remove leading and trailing whitespaces from value
            AppInf[AppInfIndex][att]=val;     # save information in hashtable
            continue;
        else:
          if line.find(identifier) != -1:
            AppInf.append({});                # initialize next dictionary
            AppInfIndex=len(AppInf) - 1;      # get index of array
          if line.find(':') == -1: continue;  # skip attribute value pair if there is no delimiter
          att, val = line.split(":",1);       # split the line in attribute and value pair
          att=att.strip();                    # remove leading and trailing whitespaces from attribute
          val=val.strip();                    # remove leading and trailing whitespaces from value
          AppInf[AppInfIndex][att]=val;       # save information in hashtable
          continue;
    else:
      continue;

  # check if there are parsed information
  if len(AppInf) == 0:
    return '';         # no information found - return NULL
  else:
    return AppInf;      # yes, we have information - return array of dictionaries


#############################################################################
# do things on the WebSphere
#############################################################################

#----------------------------------------------------------------------------
# saveAndSyncNodes
#   description: save configuration and sync nodes
#   input: -
#   return: -
#----------------------------------------------------------------------------
def saveAndSyncNodes():
  # save the changes
  AdminConfig.save();

  # sync nodes
  syncNodes();

#----------------------------------------------------------------------------
# syncNodes
#   description: sync all available nodes
#   input: -
#   return: -
#----------------------------------------------------------------------------
def syncNodes():
  nodes_list = AdminConfig.list('Node').split(lineSeparator);
  for node in nodes_list:
    nodeName = AdminConfig.showAttribute(node,'name');
    # test if node has a sync mbean
    syncMBean = AdminControl.completeObjectName('type=NodeSync,node='+ nodeName +',*');
    if syncMBean != '':
      # syn MBean found - check if node is already in sync
      if AdminControl.invoke(syncMBean, 'isNodeSynchronized') == 'false':
        # node not in sync - trigger sync
        AdminControl.invoke(syncMBean, 'sync');

#----------------------------------------------------------------------------
# start_messageListenerPort
#   description: function to start a given message listener port
#   input: serverName, listenerPortName
#   return: "true" | "false"
#----------------------------------------------------------------------------
def start_messageListenerPort(serverName, listenerPortName):
  # return if input parameters are not given to function
  if serverName == "": return "false";
  if listenerPortName == "": return "false";

  # get the MBean of the listener Port
  listenerPortMBean = AdminControl.queryNames('type=ListenerPort,name=' + listenerPortName + ',process=' + serverName + ',*');

  # if MBean is found, start the listener Port
  if listenerPortMBean != "":
    AdminControl.invoke(listenerPortMBean, 'start');
    return "true";
  else: return "false";

#----------------------------------------------------------------------------
# stop_messageListenerPort
#   description: function to stop a given message listener port
#   input: serverName, listenerPortName
#   return: "true" | "false"
#----------------------------------------------------------------------------
def stop_messageListenerPort(serverName, listenerPortName):
  # return "false" if input parameters are not given to function
  if serverName == "": return "false";
  if listenerPortName == "": return "false";

  # get the MBean of the listener Port
  listenerPortMBean = AdminControl.queryNames('type=ListenerPort,name=' + listenerPortName + ',process=' + serverName + ',*');

  # if MBean is found, stop the listener Port
  if listenerPortMBean != "":
    AdminControl.invoke(listenerPortMBean, 'stop');
    return "true";
  else: return "false";

#----------------------------------------------------------------------------
# invoke_listenerPortState
#   description: function to trigger start or stop to a given message
#     listener port ID
#   input: listenerPortID, state ('start' or 'stop')
#   return: "true" | "false"
#----------------------------------------------------------------------------
def invoke_listenerPortState(listenerPortID, state):
  if listenerPortID == "": return "false";
  state = state.lower();
  if state == 'start' or state == 'stop':
    # get the MBeanID of the listenerPort
    listenerPortMBeanID = AdminConfig.getObjectName(listenerPortID);
    # proceed if an MBean is found
    if listenerPortMBeanID != "":
      AdminControl.invoke(listenerPortMBeanID, state);
      return "true";
    else: return "false";
  else: return "false";

#----------------------------------------------------------------------------
# get_listenerPortState
#   description: function to get the current state of a given message
#     listener port
#   input: listenerPortID
#   return: "started" | "stopped" | "unknown"
#----------------------------------------------------------------------------
def get_listenerPortState(listenerPortID):
  if listenerPortID == "": return "false";
  # get the MBeanID of the listenerPort
  listenerPortMBeanID = AdminConfig.getObjectName(listenerPortID);
  # proceed if an MBean is found
  if listenerPortMBeanID != "":
    state = AdminControl.getAttribute(listenerPortMBeanID, 'started');
    if state == 'false': return 'stopped';
    elif state == 'true': return 'started';
    else: return 'unknown';
  else: return 'unknown';

#----------------------------------------------------------------------------
# get_listenerPortInitialState
#   description: function to get the initial state of a given message
#     listener port
#   input: listenerPortID
#   return: "START" | "STOP"
#----------------------------------------------------------------------------
def get_listenerPortInitialState(listenerPortID):
  if listenerPortID == "": return "false";
  else:
    return AdminConfig.showAttribute(AdminConfig.showAttribute(listenerPortID, 'stateManagement'), 'initialState');

#----------------------------------------------------------------------------
# set_listenerPortInitialState
#   description: function to set the initial state of a given message
#     listener port
#   input: listenerPortID, state ('STOP' or 'START')
#   return: "true" | "false"
#----------------------------------------------------------------------------
def set_listenerPortInitialState(listenerPortID, state):
  if listenerPortID == "": return "false";
  state = state.upper();
  if state == 'START' or state == 'STOP':
    AdminConfig.modify(AdminConfig.showAttribute(listenerPortID, 'stateManagement'), [['initialState', state]]);
    return "true";
  else: return "false";

#----------------------------------------------------------------------------
# start_applicationOnServer
#   description: starting a stopped application
#   input: string (application name), string (server Name)
#   return: "true" | "false"
#----------------------------------------------------------------------------
def start_applicationOnServer(appName, serverName):
  # return "false" if application name or server name is not given to function
  if appName == "": return "false";
  if serverName == "": return "false";

  # return "true" if the application is already started
  if get_applicationStateOnServer(appName, serverName) == "started": return "true";

  # find the application manager MBean
  cellName = AdminControl.getCell();
  appManagerMB = AdminControl.queryNames('type=ApplicationManager,cell=' + cellName + ',process=' + serverName + ',*');

  # return false if there is no application manager MBean
  if appManagerMB == "": return "false";

  # try to start application through application manager
  AdminControl.invoke(appManagerMB, 'startApplication', appName);
  return "true";


#----------------------------------------------------------------------------
# start_application
#   description: starting a stopped application
#   input: string (application name)
#   return: "true" | "false" | "partially"
#----------------------------------------------------------------------------
def start_application(appName):
  # return "false" if application name is not given to function
  if appName == "": return "false";

  RC_flag_true = "unset";
  RC_flag_false = "unset";

  # get target server members from application name
  serverNames = get_applicationTargetServerNames(appName);

  # loop over server names and start application on each server
  for serverName in serverNames:
    rc = start_applicationOnServer(appName, serverName);
    # set flag of return
    if rc == "true": RC_flag_true = "set";
    else: RC_flag_false = "set";

  # check the flags and return values
  # RC_flag_true -> application is started
  # RC_flag_false -> application is stopped
  if RC_flag_true == "set":
    if RC_flag_false == "set": return "partially";
    else: return "started";
  else:
    if RC_flag_false == "set": return "stopped";
    else: return "partially";

#----------------------------------------------------------------------------
# stop_applicationOnServer
#   description: stopping a running application
#   input: string (application name), string (server Name)
#   return: "true" | "false"
#----------------------------------------------------------------------------
def stop_applicationOnServer(appName, serverName):
  # return "false" if application name or server name is not given to function
  if appName == "": return "false";
  if serverName == "": return "false";

  # return "true" if the application is already stopped
  if get_applicationStateOnServer(appName, serverName) == "stopped": return "true";

  # find the application manager MBean
  cellName = AdminControl.getCell();
  appManagerMB = AdminControl.queryNames('type=ApplicationManager,cell=' + cellName + ',process=' + serverName + ',*');

  # return false if there is no application manager MBean
  if appManagerMB == "": return "false";

  # try to stop application through application manager
  AdminControl.invoke(appManagerMB,'stopApplication', appName);
  return "true";

#----------------------------------------------------------------------------
# stop_application
#   description: stopping a running application
#   input: string (application name)
#   return: "true" | "false" | "partially"
#----------------------------------------------------------------------------
def stop_application(appName):
  # return "false" if application name is not given to function
  if appName == "": return "false";

  RC_flag_true = "unset";
  RC_flag_false = "unset";

  # get target server members from application name
  serverNames = get_applicationTargetServerNames(appName);

  # loop over server names and start application on each server
  for serverName in serverNames:
    rc = stop_applicationOnServer(appName, serverName);
    # set flag of return
    if rc == "true": RC_flag_true = "set";
    else: RC_flag_false = "set";

  # check the flags and return values
  # RC_flag_true -> application is started
  # RC_flag_false -> application is stopped
  if RC_flag_true == "set":
    if RC_flag_false == "set": return "partially";
    else: return "stopped";
  else:
    if RC_flag_false == "set": return "started";
    else: return "partially";


#############################################################################
# POD documentation
#############################################################################

documentation = """

=pod

=head1 NAME

cybcon_was - Cybcon Industries simple python/jython WebSphere functions library

=head1 SYNOPSIS

 # export WebSphere libraries
 sys.modules['AdminConfig'] = AdminConfig;
 sys.modules['AdminControl'] = AdminControl;
 sys.modules['AdminApp'] = AdminApp;
 sys.modules['AdminTask'] = AdminTask;
 sys.modules['Help'] = Help;

 # import Cybcon Industries simple python/jython WebSphere functions library
 import cybcon_was;

 # library documentation
 doc = cybcon_was.help();
 ver = cybcon_was.version();


 # functions for text processing
 S_RC = cybcon_was.find_valueInArray(value, array);
 S_objectType = cybcon_was.get_ObjectTypeByID(objectID);
 S_objectScope = cybcon_was.get_ObjectScopeByID(objectID);

 D_MBean = cybcon_was.parse_mbean(mbean);
 A_appInfo = cybcon_was.parse_adminAppView(appName, option, identifier);

 # functions to get informations about the WebSphere Infrastructure
 A_attributes = cybcon_was.get_AttributesFromObject(objectID);
 S_value = cybcon_was.showAttribute(objectID, attribute);
 A_values = cybcon_was.splitArray(string);
 A_nodeNames cybcon_was.get_nodeNames();
 S_nodeName = cybcon_was.get_nodeNameByServerID(serverID);
 nodeAgentID = cybcon_was.get_nodeAgentID(nodeName);
 A_clusterNames = cybcon_was.get_clusterNames();
 A_serverNames = cybcon_was.get_clusterMemberNames(clusterName);
 A_serverNames = cybcon_was.get_serverMembersByNodeName(nodeName);
 A_applicationNames = cybcon_was.get_applications();
 S_srvOrCl = cybcon_was.identify_serverOrClusterByName(objectName);
 S_appState = cybcon_was.get_applicationStateOnServer(appName, serverName);
 appID = cybcon_was.get_applicationIDByName(appName);
 A_serverNames = cybcon_was.get_applicationTargetServerNames(appName);
 S_listenerPortState = cybcon_was.get_listenerPortState(listenerPortID);
 S_listenerPortInitialState = cybcon_was.get_listenerPortInitialState(listenerPortID);
 S_appState = cybcon_was.get_applicationState(appName);

 # functions to change the infrastructure
 cybcon_was.syncNodes();
 cybcon_was.saveAndSyncNodes();
 S_RC = cybcon_was.start_messageListenerPort(serverName, listenerPortName); # deprecated
 S_RC = cybcon_was.stop_messageListenerPort(serverName, listenerPortName); # deprecated
 S_RC = cybcon_was.invoke_listenerPortState(listenerPortID, S_state);    # S_state is 'start' or 'stop'
 S_RC = cybcon_was.set_listenerPortInitialState(listenerPortID, S_listenerPortInitialState);
 S_RC = cybcon_was.start_applicationOnServer(appName, serverName);
 S_RC = cybcon_was.start_application(appName);
 S_RC = cybcon_was.stop_applicationOnServer(appName, serverName);
 S_RC = cybcon_was.stop_application(appName);

=head1 REQUIRES

Jython 2.5, WebSphere Application Server 6

=head1 EXPORTS

nothing

=head1 DESCRIPTION

B<cybcon_was> is a simple python/jython WebSphere Application Server
functions library which helps you to write simple administration tools
for you're WebSphere application server environment.

The function library has three kinds of functions.

B<1st>, the text processing functions.
 This functions are small functions to parse things.

B<2nd>, the gather environment information functions.
 This functions are created to give you fast and easy access to much
often needed things in the WebSphere environment. e.g. get all node names or
get all server names on a specific node.

B<3rd>, the action items.
 This functions are created to make things on the application server. e.g. start
or stop applications or save and sync nodes.

=head1 METHODS

=head2 library documentation/help

=over 4

=item B<cybcon_was.help()>

The function "help" prints out this documentation.

=back

=head2 text processing functions

=over 4

=item B<cybcon_was.find_valueInArray(string, array)>

OK, it's a quit simple function around the python standard "if value in array".
The function searches a string in an array and gives the string "true" back if
the string is in the array or "false" if it is not.

=item B<cybcon_was.get_ObjectTypeByID(objectID)>

If you give the function a wsadmin objectID (from AdminConfig), it parses you from that
string the object type.
That object type can be used in the "AdminConfig.getid()" function to identify other objects.
example: AdminConfig.getid('/' + objectType + ':' + objectName + '/');

=item B<cybcon_was.get_ObjectScopeByID(objectID)>

If you give the function a wsadmin objectID (from AdminConfig), it tries to identify the objects scope
by parsing the ObjectID string.
You can use that to check if you are on the right scope.
The function returns following values:
  "ServerCluster"
  "Server"
  "Node"
  "Cell"
example:
  objectScope = cybcon_was.get_ObjectScopeByID(serverID)
  print objectScope will output "Server"

=item B<cybcon_was.parse_mbean(mbean)>

From the MBeans string used by AdminControl, you can gather much informations of the
location of the MBean or the corresponding object. To get a usable object of the string
representation you can use this function. It parses the MBean string and cut them into
the attribute/value pieces and store that information in a flat hashtable (dictionary),
 example:
  mbean_dict = cybcon_was.parse_mbean(mbean);
  print mbean_dict['process'];

=item B<cybcon_was.parse_adminAppView(appName, option, identifier)>

The function parses the output of AdminApp.view(appName, option) to
get the relevant information in a computer-processable way.
The relevant input parameters are the "application name", the option
(from AdminApp.options(application name)) and an identification string.
The identification string is to identify the start of a new information block.

Example:
  If you are searching for MapRolesToUsers, every new entry will start with
  the keyword 'Role:'
    appName='my_enterprise_application';
    option='MapRolesToUsers';
    identifier='Role:';
    MapRolesToUsers=cybcon_was.parse_adminAppView(appName, option, identifier);

    the Array (MapRolesToUsers) looks like:
      MapRolesToUsers[0]
       {
        'Role': 'adminRole',
        'Everyone?': 'No',
        'All authenticated?': 'No',
        'Mapped users': '',
        'Mapped groups': 'APP.ADMINS'
       }

=back

=head2 functions to get informations about the WebSphere infrastructure

=over 4

=item B<cybcon_was.get_AttributesFromObject(objectID)>

A simple function to get all available attribute names of an given objectID.
The function returns an array of that names.

=item B<cybcon_was.showAttribute(objectID, attribute)>

This function is one of the important functions in the library. It provides the
same functionality as the "AdminConfig.showAttribute" function. The difference is that
the cybcon_was.showAttribute function hase some exception prevention implemented.
So you can use this function instead to write easy code for gathering informations
about youre infrastructure without the need of exception handling.

For example, the standard AdminConfig function returns an exception if you are
requesting an attribute that not exists in an object. Resulting in an script abort from
the wsadmin interface.

In this case, the cybcon_was function returns only an empty string.

=item B<cybcon_was.splitArray(string)>

This function is an enhanced textprocessing split().
The split was made on every whitespace (SPACE) but not if the whitespace is
in parantheses.
If you read the value of an attribute and the value is an array ('[value value value]')
and one of the values has whitespaces and is in paranthese: ('[value "value with ws" value]')
the normal "split()" is not working because they split alway on the whitespace char and
ignores the parantheses. so you got an array:
['value' '"value', 'with', 'ws"', 'value']
the function cybcon_was.splitArray(string) splits into:
['value', 'value with ws', 'value']

=item B<cybcon_was.get_nodeNames()>

The functions returns an array of names of all nodes in the WebSphere cell.

=item B<cybcon_was.get_nodeNameByServerID(serverID)>

If you give that function a serverID, it tries to identify the node on which that server
is configured.
The function returns the serverName.

=item B<cybcon_was.get_nodeAgentID(nodeName)>

The function returns the objectId of the nodeAgent object which are present on the given node.

=item B<cybcon_was.get_clusterNames()>

The functions returns an array of names of all clusters in the WebSphere cell.

=item B<cybcon_was.get_clusterMemberNames(clusterName)>

The functions returns an array of server names which are members in the given cluster.

=item B<cybcon_was.get_serverMembersByNodeName(nodeName)>

The functions returns an array of server names which are members in the given node.

=item B<cybcon_was.get_applications()>

The functions returns an array of names of all applications they are installed in the application server.

=item B<cybcon_was.identify_serverOrClusterByName(objectName)>

This function guesses if the given object name is a cluster or a server name. And returns the object type
"ServerCluster" or "Server".

=item B<cybcon_was.get_applicationIDByName(appName)>

This function searches the right objectID of an application object by a given application name.

=item B<cybcon_was.get_applicationTargetServerNames(appName)>

This function get's all mapped server members on which the application is mapped.

=item B<cybcon_was.get_applicationStateOnServer(appName, serverName)>

This function determine the state of an application (identified by it's name) on a specific
server member (also identified by it's name). The application state is "started" or "stopped".

=item B<cybcon_was.get_listenerPortState(listenerPortID)>

This function determine the current state of an message adapter listener port
(identified by it's configuration object ID). The ports state is "started", "stopped" or "unknown".
You will receive an "unknown" state if there is no MBean or the MBean return no state.

=item B<cybcon_was.get_listenerPortInitialState(listenerPortID)>

This function determine the configured initial state of an message adapter listener port
(identified by it's configuration object ID). The initial ports state is "START or "STOP".

=item B<cybcon_was.get_applicationState(appName)>

This function determine the state of an application (identified by it's name) on all
server members on which the application is mapped. The application state is "started", "stopped",
"partially" or "unmapped".

=back

=head2 functions to change the infrastructure

=over 4

=item B<cybcon_was.syncNodes()>

This functions searches all managed nodes that have to be synced and sync them.

=item B<cybcon_was.saveAndSyncNodes()>

This function is an easy way to save all changes and syncronize this changes to all nodes in one step.

=item B<cybcon_was.start_messageListenerPort(serverName, listenerPortName)>

This function starts a MQ message listener port on a specific server.
If the start was initiated, the function returns a "true" and "false" if not.
This function is deprecated and will be removed in one of the next versions.
Please use function: invoke_listenerPortState(listenerPortID, S_state) instead.

=item B<cybcon_was.stop_messageListenerPort(serverName, listenerPortName)>

This function stops a MQ message listener port on a specific server.
If the stop was initiated, the function returns a "true" and "false" if not.
This function is deprecated and will be removed in one of the next versions.
Please use function: invoke_listenerPortState(listenerPortID, S_state) instead.

=item B<cybcon_was.invoke_listenerPortState(listenerPortID, S_state)>

This function is an other way to start or stop an message adapter listener port.
Input parameter is the configuration object ID of the message listener port and the
state you want to trigger.
The function returns a "true" or a "false".

=item B<cybcon_was.set_listenerPortInitialState(listenerPortID, S_listenerPortInitialState)>

This function configures the initial message adapter listener port state.
Input parameter is the configuration object ID of the message listener port and the
state you want to set ("START" or "STOP").
The function returns a "true" or a "false".

=item B<cybcon_was.start_applicationOnServer(appName, serverName)>

This function starts an application on a specific server member.
If the start was initiated, the function returns a "true" and "false" if not.

=item B<cybcon_was.stop_applicationOnServer(appName, serverName)>

This function stops an application on a specific server member.
If the stop was initiated, the function returns a "true" and "false" if not.

=item B<cybcon_was.start_application(appName)>

This function starts an application on all mapped server members.
If the start was initiated, the function returns a "true" and "false" if not.
If some starts where initiated and some not, the function returns a "partially".

=item B<cybcon_was.stop_application(appName)>

This function stops an application on all mapped server members.
If the stop was initiated, the function returns a "true" and "false" if not.
If some stops where initiated and some not, the function returns a "partially".

=back

=head1 EXAMPLES

=head2 initialize the library

 # import standard modules
 import time;                                    # module for date and time
 import sys;                                     # system libraries

 # export WebSphere libraries
 sys.modules['AdminConfig'] = AdminConfig;
 sys.modules['AdminControl'] = AdminControl;
 sys.modules['AdminApp'] = AdminApp;
 sys.modules['AdminTask'] = AdminTask;
 sys.modules['Help'] = Help;

 # import special libraries
 sys.path.append('/path/to/cybcon/libs');        # set additional library path
 import cybcon_was;                              # module with usefull functions

=head2 get an short infrastructure outline

 print "WAS cell: " + AdminControl.getCell();
 for clusterName in cybcon_was.get_clusterNames():
   print "  WAS cluster: " + clusterName;
   for serverName in cybcon_was.get_clusterMemberNames(clusterName):
     print "    WAS server member: " + serverName;
 for nodeName in get_nodeNames():
   print "  WAS node: " + nodeName;
   for serverName in cybcon_was.get_serverMembersByNodeName(nodeName):
     print "    WAS server member: " + serverName;


=head2 get an state of all installed applications

 for appName in cybcon_was.get_applications():
   appName + ": [" + cybcon_was.get_applicationState(appName) + "]";

=head1 BUGS

No bugs known!   :-)

Please report bugs to Michael Oberdorf <cybcon@cybcon-industries.de>

=head1 SEE ALSO

The very good IBM WebSphere documentation about jython programming. *rofl*

=head1 AUTHOR

Michael Oberdorf <cybcon@cybcon-industries.de>

Cybcon Industries <http://www.cybcon-industries.de/>

=head1 COPYRIGHT AND LICENSE

(C) Copyright 2009, Cybcon Industries, Michael Oberdorf <cybcon@cybcon-industries.de>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to
deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.

=cut

"""
