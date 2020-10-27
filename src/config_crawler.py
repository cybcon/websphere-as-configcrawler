################################################################################
# WebSphere configuration crawler
# description: script to crawl the WAS configuration and output them to
#
# Author: Michael Oberdorf
# Date: 2009-05-15
# Tool can be downloaded at: http://www.cybcon-industries.de/
#-------------------------------------------------------------------------------
# COPYRIGHT AND LICENSE
#
# (C) Copyright 2009-2013, Cybcon Industries, Michael Oberdorf <cybcon@cybcon-industries.de>
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
#  $Revision: 24 $
#  $LastChangedDate: 2014-03-17 16:44:21 +0100 (Mon, 17 Mar 2014) $
#  $LastChangedBy: cybcon89 $
#  $Id: config_crawler.py 24 2014-03-17 15:44:21Z cybcon89 $
################################################################################

#----------------------------------------------------------------------------
# Definition of global variables
#----------------------------------------------------------------------------

# version of this script
VERSION="0.579";

# import standard modules
import time;                                      # module for date and time
import sys;                                       # system libraries
import java.lang.System;                          # java system library

# set configuration file from command line or set default
if len(sys.argv) != 1:
  configFile="/tmp/crawler.conf";
else:
  configFile=sys.argv[0];

# set the valid keys for the output function
validOutKeys = ['name', 'value', 'description', 'unit', 'tagname', 'tagtype', 'tagprops'];

# formating whitespace chars for text output
textSpaceCounter=0;
textSpaceOffset=2;

# set the line separator variable
lineSeparator = java.lang.System.getProperty('line.separator');

#############################################################################
# FUNCTIONS
#############################################################################

#----------------------------------------------------------------------------
# get_configuration
#   description: opens a configuration file and parse it, return the
#     configuration object
#   input: path and filename as string
#   return: associative array:
#     array[section][attribute] = value
#----------------------------------------------------------------------------
def get_configuration(configfile):
# set the variable to hold configuration file
  configHash = {};
# set other variables
  section = "";

# open the configuration file
  FH = open(configfile, "r");

# parse copnfiguration file
  for line in FH.readlines():
#   remove leading and trailing whitespaces
    line = line.strip();
#   ignore empty lines and comment lines
    if line == "": continue;
    if line[0] == "#": continue;
#   find a new section
    if line[0] == "[":
      section = line.lower().replace("[", "").replace("]", "").strip();
#     define section as dictionare
      configHash[section] = {};
      continue;
#   all other lines are attribute/value pairs
#   split at equal char, and set value to lower case
    attribute, value = line.split("=",1);
    value = value.lower();
#   if we are in a section, and an attribute is set append attribute/value pair to section
    if section != "" and attribute != "":
      configHash[section][attribute] = value;

# after parsing the file, close the file
  FH.close();

#-----------------------
# prevent errors by checking the attributes

# possible sections in config file
  configSections = ['general', 'services', 'cell', 'cluster', 'application', 'node', 'dmgr', 'nodeagent', 'appserver', 'webserver', 'cybcon_was'];
# possible attributes in config file
  configAttributes = {};
  configAttributes['general'] = ['services', 'cell', 'cluster', 'node', 'dmgr', 'nodeagent', 'appserver', 'webserver', 'application', 'LogPasswords', 'output_format'];
  configAttributes['services'] = ['serviceProviders', 'policySets'];
  configAttributes['cell'] = ['CoreGroup', 'JMS_provider', 'JDBC_provider', 'ResourceAdapter', 'AsyncBeans', 'CacheInstances', 'Mail_provider', 'URL_provider', 'ResourceEnv', 'Security', 'Virtual_hosts', 'Websphere_variables', 'Shared_libraries', 'NameSpaceBindings', 'CORBANamingService', 'SIBus'];
  configAttributes['cluster'] = ['clusterMembers', 'JMS_provider', 'JDBC_provider', 'ResourceAdapter', 'AsyncBeans', 'CacheInstances', 'Mail_provider', 'URL_provider', 'ResourceEnv', 'Websphere_variables', 'Shared_libraries'];
  configAttributes['application'] = ['targetMapping', 'runState', 'startupBehavior', 'binaries', 'classLoader', 'requestDispatcher', 'sharedLibRef', 'sessionManagement', 'jSPAndJSFoptions'];
  configAttributes['node'] = ['WAS_version', 'OS_name', 'hostname', 'JMS_provider', 'JDBC_provider', 'ResourceAdapter', 'AsyncBeans', 'CacheInstances', 'Mail_provider', 'URL_provider', 'ResourceEnv', 'Websphere_variables', 'Shared_libraries', 'NameSpaceBindings'];
  configAttributes['dmgr'] = ['JVM_properties', 'EndPointPorts', 'DCSTransports', 'HAManagerService', 'Logging'];
  configAttributes['nodeagent'] = ['JVM_properties', 'EndPointPorts', 'DCSTransports', 'HAManagerService', 'Sync_service', 'Logging'];
  configAttributes['appserver'] = ['ApplicationServerProperties', 'JVM_properties', 'EndPointPorts', 'DCSTransports', 'MSGListenerPorts', 'JMS_provider', 'HAManagerService', 'JDBC_provider', 'ResourceAdapter', 'AsyncBeans', 'CacheInstances', 'Mail_provider', 'URL_provider', 'ResourceEnv', 'Websphere_variables', 'Shared_libraries', 'NameSpaceBindings', 'Logging'];
  configAttributes['webserver'] = ['WebServerProperties', 'EndPointPorts', 'Logging', 'Plugin_properties', 'RemoteWebServerMgmnt', 'Websphere_variables'];
  configAttributes['cybcon_was'] = [ 'libPath', 'minVersion' ];
# default value
  configDefaultValue="false";

# loop over configuration and set default values if they are not exist
  for section in configSections:
    if configHash.has_key(section) != 1:
      # set section key
      configHash[section] = {};
    for attribute in configAttributes[section]:
      if configHash[section].has_key(attribute) != 1:
        # set attribute key with default option
        configHash[section][attribute] = configDefaultValue;

  # set default output format
  if configHash['general']['output_format'] != "xml": configHash['general']['output_format'] = "text";

  # set defaults for cybcon_was library
  if configHash['cybcon_was']['libPath'] == "false": configHash['cybcon_was']['libPath'] = "./";
  if configHash['cybcon_was']['minVersion'] == "false": configHash['cybcon_was']['minVersion'] = "1.021";

# give configuration object back
  return configHash;

#----------------------------------------------------------------------------
# dataOut
#   description: printout the given data in text or xml format (depends on
#     CONFIG['general']['output_format'])
#   input: dictionary
#     dictonary keys are:
#       'name'        (WAS attribute name)
#       'value'       (WAS attribute value)
#       'description' (WAS attribute description)
#       'unit'        (optional unit of an value)
#       'tagname'     (XML: tag name)
#       'tagtype'     (XML: 0=<open>val</close>; 1=<open>; 2=</close>; 3=<single />)
#       'tagprops'    (array of tag specific properties)
#   output: string
#   return: -
#----------------------------------------------------------------------------
def dataOut(DATA):
  # register globals
  global textSpaceCounter;

  # loop over possible dictonary keys and define unset keys
  for key in validOutKeys:
    if DATA.has_key(key) != 1: DATA[key] = "";
  # set default values
  if DATA['name'] == "":         DATA['name'] = "";
  if DATA['value'] == "":        DATA['value'] = "";
  if DATA['description'] == "":  DATA['description'] = "";
  if DATA['unit'] == "":         DATA['unit'] = "";
  if DATA['tagname'] == "":      DATA['tagname'] = "";
  if DATA['tagtype'] == "":      DATA['tagtype'] = "0";
  if DATA['tagprops'] == "":     DATA['tagprops'] = [];

  # set whitespaces prefix
  if DATA['tagtype'] == "2": textSpaceCounter = textSpaceCounter - textSpaceOffset;
  wsPrefix = "";
  for i in range(textSpaceCounter):
    wsPrefix = wsPrefix + " ";

  # MASK security specific data if needed
  if CONFIG['general']['LogPasswords'] != "true":
    if DATA['description'].lower().find("password") != -1:
      DATA['value'] = "***skipped by policy***";

  # process xml specific output
  if CONFIG['general']['output_format'] == "xml":
    if DATA['tagname'] != "":
      DATA['tagname'] = DATA['tagname'].lower();
      xmlString = wsPrefix;
      if DATA['tagtype'] == "0":
        xmlString = xmlString + "<" + DATA['tagname'];
        if DATA['description'] != "": xmlString = xmlString + " description='" + DATA['description'] + "'";
        if DATA['name'] != "": xmlString = xmlString + " name='" + DATA['name'] + "'";
        if DATA['unit'] != "": xmlString = xmlString + " unit='" + DATA['unit'] + "'";
        for tagProp in DATA['tagprops']: xmlString = xmlString + " " + tagProp;
        xmlString = xmlString + ">";
        if DATA['value'].find("<") != -1 or DATA['value'].find(">") != -1 or DATA['value'].find("&") != -1:
          xmlString = xmlString + "<![CDATA[" + DATA['value'] + "]]></" + DATA['tagname'] + ">";
        else:
          xmlString = xmlString + DATA['value'] + "</" +  DATA['tagname'] + ">";
      elif DATA['tagtype'] == "1":
        xmlString = xmlString + "<" + DATA['tagname'];
        if DATA['description'] != "": xmlString = xmlString + " description='" + DATA['description'] + "'";
        if DATA['name'] != "": xmlString = xmlString + " name='" + DATA['name'] + "'";
        if DATA['value'] != "": xmlString = xmlString + " value='" + DATA['value'] + "'";
        if DATA['unit'] != "": xmlString = xmlString + " unit='" + DATA['unit'] + "'";
        for tagProp in DATA['tagprops']: xmlString = xmlString + " " + tagProp;
        xmlString = xmlString + ">";
      elif DATA['tagtype'] == "2":
        xmlString = xmlString + "</" + DATA['tagname'] + ">";
      elif DATA['tagtype'] == "3":
        xmlString = xmlString + "<" + DATA['tagname'];
        if DATA['description'] != "": xmlString = xmlString + " description='" + DATA['description'] + "'";
        if DATA['name'] != "": xmlString = xmlString + " name='" + DATA['name'] + "'";
        if DATA['value'] != "": xmlString = xmlString + " value='" + DATA['value'] + "'";
        if DATA['unit'] != "": xmlString = xmlString + " unit='" + DATA['unit'] + "'";
        for tagProp in DATA['tagprops']: xmlString = xmlString + " " + tagProp;
        xmlString = xmlString + " />";
      print xmlString;
      # set follow up textSpaceCounter
      if DATA['tagtype'] == "1":   textSpaceCounter = textSpaceCounter + textSpaceOffset;
  
  # process text specific output
  else:
    if DATA['tagtype'] == "2":
      print "";
    else:
      if DATA['description'] != "" or DATA['value'] != "":
        if DATA['description'] != "":
          print wsPrefix + DATA['description'] + ": " + DATA['value'] + " " + DATA['unit'];
        else:
          print wsPrefix + DATA['value'] + " " + DATA['unit'];
        for tagProp in DATA['tagprops']:
          print wsPrefix + "  " + tagProp.replace("='", ": ").replace("'", "");
      # set follow up textSpaceCounter
      if DATA['tagtype'] == "1":   textSpaceCounter = textSpaceCounter + textSpaceOffset;

#----------------------------------------------------------------------------
# get_nodeAgentSyncServiceProperties
#   description: output the sync service properties configured in the node
#     agent
#   input: nodeName
#   output: informations on stdout
#   return: -
#----------------------------------------------------------------------------
def get_nodeAgentSyncServiceProperties(nodeName):
  nodeAgentID = cybcon_was.get_nodeAgentID(nodeName);
  dataOut({'description': "Additional Properties", 'tagname': "additionalproperties", 'tagtype': "1"});
  fSSID = cybcon_was.showAttribute(nodeAgentID, 'fileSynchronizationService');
  dataOut({'description': "File synchronization service", 'tagname': "filesynchronizationservice", 'tagtype': "1"});
  dataOut({'description': "General Properties", 'tagname': "generalproperties", 'tagtype': "1"});
  dataOut({'name': "enable", 'value': cybcon_was.showAttribute(fSSID, 'enable'), 'description': "Enable service at server startup", 'tagname': "enable"});
  dataOut({'name': "synchInterval", 'value': cybcon_was.showAttribute(fSSID, 'synchInterval'), 'unit': "minutes", 'description': "Synchronization interval", 'tagname': "synchInterval"});
  dataOut({'name': "autoSynchEnabled", 'value': cybcon_was.showAttribute(fSSID, 'autoSynchEnabled'), 'description': "Automatic synchronization", 'tagname': "autoSynchEnabled"});
  dataOut({'name': "synchOnServerStartup", 'value': cybcon_was.showAttribute(fSSID, 'synchOnServerStartup'), 'description': "Startup synchronization", 'tagname': "synchOnServerStartup"});
  dataOut({'tagname': "generalproperties", 'tagtype': "2"});
  dataOut({'tagname': "filesynchronizationservice", 'tagtype': "2"});
  dataOut({'tagname': "additionalproperties", 'tagtype': "2"});

#----------------------------------------------------------------------------
# get_CoreGroupProperties
#   description: output the core group properties on the given objectID
#     level
#   input: cellID
#   output: informations on stdout
#   return: -
#----------------------------------------------------------------------------
def get_CoreGroupProperties(cellID):
  dataOut({'description': "Core groups", 'tagname': "coregroups", 'tagtype': "1"});
  dataOut({'description': "Core group settings", 'tagname': "coregroupsettings", 'tagtype': "1"});

  for coreGroupID in AdminConfig.list("CoreGroup", cellID).split(lineSeparator):
    dataOut({'name': "name", 'value': cybcon_was.showAttribute(coreGroupID, 'name'), 'description': "Name", 'tagname': "name"});
    dataOut({'name': "description", 'value': cybcon_was.showAttribute(coreGroupID, 'description'), 'description': "Description", 'tagname': "description"});
    dataOut({'name': "numCoordinators", 'value': cybcon_was.showAttribute(coreGroupID, 'numCoordinators'), 'description': "Number of coordinators", 'tagname': "numCoordinators"});
    dataOut({'name': "transportType", 'value': cybcon_was.showAttribute(coreGroupID, 'transportType'), 'description': "Transport type", 'tagname': "transportType"});

    dataOut({'description': "Core group servers", 'tagname': "coregroupservers", 'tagtype': "1"});
    coreGroupServerID=""
    for coreGroupServerID in cybcon_was.splitArray(cybcon_was.showAttribute(coreGroupID, 'coreGroupServers')):
      dataOut({'tagname': "coregroupserver", 'tagtype': "1"});
      dataOut({'name': "serverName", 'value': cybcon_was.showAttribute(coreGroupServerID, 'serverName'), 'description': "Name", 'tagname': "servername"});
      dataOut({'name': "nodeName", 'value': cybcon_was.showAttribute(coreGroupServerID, 'nodeName'), 'description': "Node", 'tagname': "nodename"});
      dataOut({'tagname': "coregroupserver", 'tagtype': "2"});
    if coreGroupServerID == "":
      dataOut({'description': "WARNING", 'value': "No Core Group Servers defined in Core Group."});
    dataOut({'tagname': "coregroupservers", 'tagtype': "2"});

    dataOut({'description': "Custom properties", 'tagname': "customproperties", 'tagtype': "1"});
    CusProp="";
    for CusProp in cybcon_was.splitArray(cybcon_was.showAttribute(coreGroupID, 'customProperties')):
      dataOut({'name': "customProperty", 'value': cybcon_was.showAttribute(CusProp, 'value'), 'description': cybcon_was.showAttribute(CusProp, 'name'), 'tagname': "property"});
    if CusProp == "":
      dataOut({'value': "No custom properties set."});
    dataOut({'tagname': "customproperties", 'tagtype': "2"});

    dataOut({'description': "Preferred coordinator servers", 'tagname': "preferedcoordinatorservers", 'tagtype': "1"});
    prefCordSrvID="";
    for prefCordSrvID in cybcon_was.splitArray(cybcon_was.showAttribute(coreGroupID, 'preferredCoordinatorServers')):
      dataOut({'tagname': "preferedcoordinatorserver", 'tagtype': "1"});
      dataOut({'name': "serverName", 'value': cybcon_was.showAttribute(prefCordSrvID, 'serverName'), 'description': "Name", 'tagname': "servername"});
      dataOut({'name': "nodeName", 'value': cybcon_was.showAttribute(prefCordSrvID, 'nodeName'), 'description': "Node", 'tagname': "nodename"});
      dataOut({'tagname': "preferedcoordinatorserver", 'tagtype': "2"});
    if prefCordSrvID == "":
      dataOut({'description': "WARNING", 'value': "No prefered coordinator servers defined in Core Group."});
    dataOut({'tagname': "preferedcoordinatorservers", 'tagtype': "2"});
  dataOut({'tagname': "coregroupsettings", 'tagtype': "2"});

  dataOut({'description': "Core group bridge settings", 'tagname': "coregroupbridgesettings", 'tagtype': "1"});
  for coreGroupBridgeID in cybcon_was.splitArray(AdminConfig.list("CoreGroupBridgeSettings", cellID)):
    dataOut({'description': "Access point groups", 'tagname': "accesspointgroups", 'tagtype': "1"});
    apgID="";
    for apgID in cybcon_was.splitArray(cybcon_was.showAttribute(coreGroupBridgeID, 'accessPointGroups')):
      dataOut({'tagname': "accesspointgroup", 'tagtype': "1"});
      dataOut({'name': "name", 'value': cybcon_was.showAttribute(apgID, 'name'), 'description': "Name", 'tagname': "name"});
      dataOut({'description': "Core group access points", 'tagname': "coregroupaccesspoints", 'tagtype': "1"});
      cgapID="";
      for cgapID in cybcon_was.splitArray(cybcon_was.showAttribute(apgID, 'coreGroupAccessPointRefs')):
        dataOut({'tagname': "coregroupaccesspoint", 'tagtype': "1"});
        dataOut({'name': "name", 'value': cybcon_was.showAttribute(cgapID, 'name'), 'description': "Name", 'tagname': "name"});
        dataOut({'name': "coreGroup", 'value': cybcon_was.showAttribute(cgapID, 'coreGroup'), 'description': "Core Group", 'tagname': "coregroup"});
        dataOut({'description': "Bridge interfaces", 'tagname': "bridgeinterfaces", 'tagtype': "1"});
        cgbiID="";
        for cgbiID in cybcon_was.splitArray(cybcon_was.showAttribute(cgapID, 'bridgeInterfaces')):
          dataOut({'tagname': "bridgeinterface", 'tagtype': "1"});
          dataOut({'name': "node", 'value': cybcon_was.showAttribute(cgbiID, 'node'), 'description': "Node", 'tagname': "node"});
          dataOut({'name': "server", 'value': cybcon_was.showAttribute(cgbiID, 'server'), 'description': "Server", 'tagname': "server"});
          dataOut({'name': "chain", 'value': cybcon_was.showAttribute(cgbiID, 'chain'), 'description': "Chain", 'tagname': "chain"});
          dataOut({'tagname': "bridgeinterface", 'tagtype': "2"});
        if cgbiID == "":
          dataOut({'value': "No bridge interfaces defined in this core group access point."});
        dataOut({'tagname': "bridgeinterfaces", 'tagtype': "2"});
        dataOut({'tagname': "coregroupaccesspoint", 'tagtype': "2"});
      if cgapID == "":
        dataOut({'description': "WARNING", 'value': "No Core group access points defined in this access point group."});
      dataOut({'tagname': "coregroupaccesspoints", 'tagtype': "2"});
      dataOut({'tagname': "accesspointgroup", 'tagtype': "2"});
    if apgID == "":
      dataOut({'description': "WARNING", 'value': "No access point groups defined in Core Group Bridge."});
    dataOut({'tagname': "accesspointgroups", 'tagtype': "2"});
  dataOut({'tagname': "coregroupbridgesettings", 'tagtype': "2"});
  dataOut({'tagname': "coregroups", 'tagtype': "2"});

#----------------------------------------------------------------------------
# get_JMSProviderProperties
#   description: output the JMS provider properties on the given objectID
#     level
#   input: objectID (can be cellID, clusterID, nodeID or serverID)
#   output: informations on stdout
#   return: -
#----------------------------------------------------------------------------
def get_JMSProviderProperties(objectID):
  dataOut({'description': "JMS Providers", 'tagname': "jmsproviders", 'tagtype': "1"});
  # get name and objectType of the objectID
  objectName = cybcon_was.showAttribute(objectID, 'name');
  objectType = cybcon_was.get_ObjectTypeByID(objectID);
  if objectType == "Server":
    nodeName = cybcon_was.get_nodeNameByServerID(objectID);
    if nodeName != "": objectType = 'Node:' + nodeName + '/' + objectType;

  #-----------------------
  # Default messaging provider
  dataOut({'description': "Default messaging provider", 'tagname': "defaultmessaging", 'tagtype': "1"});
  #JMSProviderID = AdminConfig.getid('/' + objectType + ':' + objectName + '/JMSProvider:WebSphere JMS Provider/');
  JMSProviderID = AdminConfig.getid('/' + objectType + ':' + objectName + '/J2CResourceAdapter:SIB JMS Resource Adapter/');
  #JMSProviderID="";
  #for JMSProviderID_tmp in AdminConfig.list('J2CResourceAdapter', objectID).split(lineSeparator):
  #  if cybcon_was.showAttribute(JMSProviderID_tmp, 'name') == "SIB JMS Resource Adapter":
  #    JMSProviderID=JMSProviderID_tmp;
  if JMSProviderID != "":
    dataOut({'description': "Queue connection factories", 'tagname': "queueconnectionfactories", 'tagtype': "1"});
    for QCF in AdminConfig.list('J2CConnectionFactory', JMSProviderID).split(lineSeparator):
      if QCF != "":
        conDefID = cybcon_was.showAttribute(QCF, 'connectionDefinition');
        if conDefID != "":
          if cybcon_was.showAttribute(conDefID, 'connectionInterface') != "javax.jms.QueueConnection": continue;
        else: continue;
        dataOut({'tagname': "queueconnectionfactory", 'tagtype': "1"});
        dataOut({'name': "name", 'value': cybcon_was.showAttribute(QCF, 'name'), 'description': "Name", 'tagname': "name"});
        dataOut({'name': "jndiName", 'value': cybcon_was.showAttribute(QCF, 'jndiName'), 'description': "JNDI name", 'tagname': "jndiname"});
        conDefID = cybcon_was.showAttribute(QCF, 'connectionDefinition');
        # parse connection definitions config properties
        conDefProp = {};
        for conDefPropID in cybcon_was.splitArray(cybcon_was.showAttribute(conDefID, 'configProperties')):
          if conDefPropID != "":
            propName=cybcon_was.showAttribute(conDefPropID, 'name');
            propValue=cybcon_was.showAttribute(conDefPropID, 'value');
            # propDesc=cybcon_was.showAttribute(conDefPropID, 'description');
            # propType=cybcon_was.showAttribute(conDefPropID, 'type');
            conDefProp[propName] = propValue;
        if conDefProp.has_key('BusName') == 0: conDefProp['BusName'] = "";
        dataOut({'name': "value", 'value': conDefProp['BusName'], 'description': "Bus name", 'tagname': "busname"});
        if conDefProp.has_key('Target') == 0: conDefProp['Target'] = "";
        dataOut({'name': "value", 'value': conDefProp['Target'], 'description': "Target", 'tagname': "target"});
        if conDefProp.has_key('TargetType') == 0: conDefProp['TargetType'] = "";
        dataOut({'name': "value", 'value': conDefProp['TargetType'], 'description': "Target type", 'tagname': "TargetType"});
        if conDefProp.has_key('TargetSignificance') == 0: conDefProp['TargetSignificance'] = "";
        dataOut({'name': "value", 'value': conDefProp['TargetSignificance'], 'description': "Target significance", 'tagname': "TargetSignificance"});
        if conDefProp.has_key('TargetTransportChain') == 0: conDefProp['TargetTransportChain'] = "";
        dataOut({'name': "value", 'value': conDefProp['TargetTransportChain'], 'description': "Target inbound transport chain", 'tagname': "TargetTransportChain"});
        if conDefProp.has_key('ProviderEndpoints') == 0: conDefProp['ProviderEndpoints'] = "";
        dataOut({'name': "value", 'value': conDefProp['ProviderEndpoints'], 'description': "Provider endpoints", 'tagname': "ProviderEndpoints"});
        if conDefProp.has_key('ConnectionProximity') == 0: conDefProp['ConnectionProximity'] = "";
        dataOut({'name': "value", 'value': conDefProp['ConnectionProximity'], 'description': "Connection proximity", 'tagname': "ConnectionProximity"});
        if conDefProp.has_key('NonPersistentMapping') == 0: conDefProp['NonPersistentMapping'] = "";
        dataOut({'name': "value", 'value': conDefProp['NonPersistentMapping'], 'description': "Nonpersistent message reliability", 'tagname': "NonPersistentMapping"});
        if conDefProp.has_key('PersistentMapping') == 0: conDefProp['PersistentMapping'] = "";
        dataOut({'name': "value", 'value': conDefProp['PersistentMapping'], 'description': "Persistent message reliability", 'tagname': "PersistentMapping"});
        if conDefProp.has_key('ReadAhead') == 0: conDefProp['ReadAhead'] = "";
        dataOut({'name': "value", 'value': conDefProp['ReadAhead'], 'description': "Read ahead", 'tagname': "ReadAhead"});
        if conDefProp.has_key('TemporaryQueueNamePrefix') == 0: conDefProp['TemporaryQueueNamePrefix'] = "";
        dataOut({'name': "value", 'value': conDefProp['TemporaryQueueNamePrefix'], 'description': "Temporary queue name prefix", 'tagname': "TemporaryQueueNamePrefix"});
        dataOut({'name': "authDataAlias", 'value': cybcon_was.showAttribute(QCF, 'authDataAlias'), 'description': "Component-managed authentication alias", 'tagname': "authDataAlias"});
        dataOut({'name': "logMissingTransactionContext", 'value': cybcon_was.showAttribute(QCF, 'logMissingTransactionContext'), 'description': "Log missing transaction contexts", 'tagname': "logMissingTransactionContext"});
        dataOut({'name': "manageCachedHandles", 'value': cybcon_was.showAttribute(QCF, 'manageCachedHandles'), 'description': "Manage cached handles", 'tagname': "manageCachedHandles"});
        if conDefProp.has_key('ShareDataSourceWithCMP') == 0: conDefProp['ShareDataSourceWithCMP'] = "";
        dataOut({'name': "value", 'value': conDefProp['ShareDataSourceWithCMP'], 'description': "Share data source with CMP", 'tagname': "ShareDataSourceWithCMP"});
        dataOut({'name': "xaRecoveryAuthAlias", 'value': cybcon_was.showAttribute(QCF, 'xaRecoveryAuthAlias'), 'description': "XA recovery authentication alias", 'tagname': "xaRecoveryAuthAlias"});

        dataOut({'description': "Connection pool properties", 'tagname': "connectionpool", 'tagtype': "1"});
        QCF_CPID = cybcon_was.showAttribute(QCF, 'connectionPool');
        if QCF_CPID != "":
          dataOut({'name': "connectionTimeout", 'value': cybcon_was.showAttribute(QCF_CPID, 'connectionTimeout'), 'unit': "seconds", 'description': "Connection timeout", 'tagname': "connectiontimeout"});
          dataOut({'name': "maxConnections", 'value': cybcon_was.showAttribute(QCF_CPID, 'maxConnections'), 'unit': "connections", 'description': "Maximum connections", 'tagname': "maxconnections"});
          dataOut({'name': "minConnections", 'value': cybcon_was.showAttribute(QCF_CPID, 'minConnections'), 'unit': "connections", 'description': "Minimum connections", 'tagname': "minconnections"});
          dataOut({'name': "reapTime", 'value': cybcon_was.showAttribute(QCF_CPID, 'reapTime'), 'unit': "seconds", 'description': "Reap time", 'tagname': "reaptime"});
          dataOut({'name': "unusedTimeout", 'value': cybcon_was.showAttribute(QCF_CPID, 'unusedTimeout'), 'unit': "seconds", 'description': "Unused timeout", 'tagname': "unusedtimeout"});
          dataOut({'name': "agedTimeout", 'value': cybcon_was.showAttribute(QCF_CPID, 'agedTimeout'), 'unit': "seconds", 'description': "Aged timeout", 'tagname': "agedtimeout"});
          dataOut({'name': "purgePolicy", 'value': cybcon_was.showAttribute(QCF_CPID, 'purgePolicy'), 'description': "Purge policy", 'tagname': "purgepolicy"});
        else:
          dataOut({'description': "WARNING", 'value': "No connection pool configuration object found - skip connection pool properties!"});
        dataOut({'tagname': "connectionpool", 'tagtype': "2"});
        dataOut({'tagname': "queueconnectionfactory", 'tagtype': "2"});
      else:
        dataOut({'value': "No queue connection factory defined on this scope."});
    dataOut({'tagname': "queueconnectionfactories", 'tagtype': "2"});

    dataOut({'description': "Queues", 'tagname': "queues", 'tagtype': "1"});
    for queue in AdminConfig.list('J2CAdminObject', JMSProviderID).split(lineSeparator):
      if queue != "":
        dataOut({'tagname': "j2cadminobject", 'tagtype': "1"});
        dataOut({'name': "name", 'value': cybcon_was.showAttribute(queue, 'name'), 'description': "Name", 'tagname': "name"});
        dataOut({'name': "jndiName", 'value': cybcon_was.showAttribute(queue, 'jndiName'), 'description': "JNDI name", 'tagname': "jndiname"});
        dataOut({'name': "description", 'value': cybcon_was.showAttribute(queue, 'description'), 'description': "description", 'tagname': "description"});
        # parse queue properties
        queueProp = {};
        for propID in cybcon_was.splitArray(cybcon_was.showAttribute(queue, 'properties')):
          if propID != "":
            propName=cybcon_was.showAttribute(propID, 'name');
            propValue=cybcon_was.showAttribute(propID, 'value');
            # propReq=cybcon_was.showAttribute(conDefPropID, 'required');
            # propType=cybcon_was.showAttribute(conDefPropID, 'type');
            queueProp[propName] = propValue;
        if queueProp.has_key('BusName') == 0: queueProp['BusName'] = "";
        dataOut({'name': "value", 'value': queueProp['BusName'], 'description': "Bus name", 'tagname': "busname"});
        if queueProp.has_key('QueueName') == 0: queueProp['QueueName'] = "";
        dataOut({'name': "value", 'value': queueProp['QueueName'], 'description': "Queue name", 'tagname': "QueueName"});
        if queueProp.has_key('DeliveryMode') == 0: queueProp['DeliveryMode'] = "";
        dataOut({'name': "value", 'value': queueProp['DeliveryMode'], 'description': "Delivery mode", 'tagname': "DeliveryMode"});
        if queueProp.has_key('TimeToLive') == 0: queueProp['TimeToLive'] = "";
        dataOut({'name': "value", 'value': queueProp['TimeToLive'], 'description': "Time to live", 'unit': "milliseconds", 'tagname': "TimeToLive"});
        if queueProp.has_key('Priority') == 0: queueProp['Priority'] = "";
        dataOut({'name': "value", 'value': queueProp['Priority'], 'description': "Priority", 'tagname': "Priority"});
        if queueProp.has_key('ReadAhead') == 0: queueProp['ReadAhead'] = "";
        dataOut({'name': "value", 'value': queueProp['ReadAhead'], 'description': "Read ahead", 'tagname': "ReadAhead"});
        dataOut({'tagname': "j2cadminobject", 'tagtype': "2"});
      else:
        dataOut({'value': "No queues defined on this scope."});
    dataOut({'tagname': "queues", 'tagtype': "2"});

  dataOut({'tagname': "defaultmessaging", 'tagtype': "2"});

  #-----------------------
  # WebSphere MQ messaging provider
  dataOut({'description': "WebSphere MQ", 'tagname': "webspheremq", 'tagtype': "1"});
  JMSProviderID = AdminConfig.getid('/' + objectType + ':' + objectName + '/JMSProvider:WebSphere MQ JMS Provider/');
  #JMSProviderID="";
  #for JMSProviderID_tmp in AdminConfig.list('JMSProvider', objectID).split(lineSeparator):
  #  if cybcon_was.showAttribute(JMSProviderID_tmp, 'name') == "WebSphere MQ JMS Provider":
  #    JMSProviderID=JMSProviderID_tmp;
  if JMSProviderID != "":
    dataOut({'description': "WebSphere MQ queue connection factories", 'tagname': "mqqueueconnectionfactories", 'tagtype': "1"});
    for MQQCF in AdminConfig.list('MQQueueConnectionFactory', JMSProviderID).split(lineSeparator):
      if MQQCF != "":
        dataOut({'tagname': "mqqueueconnectionfactory", 'tagtype': "1"});
        dataOut({'name': "name", 'value': cybcon_was.showAttribute(MQQCF, 'name'), 'description': "Name", 'tagname': "name"});
        dataOut({'name': "jndiName", 'value': cybcon_was.showAttribute(MQQCF, 'jndiName'), 'description': "JNDI name", 'tagname': "jndiname"});
        dataOut({'name': "mappingConfigAlias", 'value': cybcon_was.showAttribute(cybcon_was.showAttribute(MQQCF, 'mapping'), 'mappingConfigAlias'), 'description': "Mapping-configuration alias", 'tagname': "mappingConfigAlias"});
        dataOut({'name': "queueManager", 'value': cybcon_was.showAttribute(MQQCF, 'queueManager'), 'description': "Queue manager", 'tagname': "queuemanager"});
        dataOut({'name': "host", 'value': cybcon_was.showAttribute(MQQCF, 'host'), 'description': "Host", 'tagname': "host"});
        dataOut({'name': "port", 'value': cybcon_was.showAttribute(MQQCF, 'port'), 'description': "Port", 'tagname': "port"});
        dataOut({'name': "channel", 'value': cybcon_was.showAttribute(MQQCF, 'channel'), 'description': "Channel", 'tagname': "channel"});
        dataOut({'name': "transportType", 'value': cybcon_was.showAttribute(MQQCF, 'transportType'), 'description': "Transport Type", 'tagname': "transportType"});
        dataOut({'name': "msgRetention", 'value': cybcon_was.showAttribute(MQQCF, 'msgRetention'), 'description': "Enable message retention", 'tagname': "msgRetention"});
        dataOut({'name': "XAEnabled", 'value': cybcon_was.showAttribute(MQQCF, 'XAEnabled'), 'description': "Enable XA", 'tagname': "XAEnabled"});
        dataOut({'name': "useConnectionPooling", 'value': cybcon_was.showAttribute(MQQCF, 'useConnectionPooling'), 'description': "Enable MQ connection pooling", 'tagname': "useConnectionPooling"});

        dataOut({'description': "Custom properties", 'tagname': "customproperties", 'tagtype': "1"});
        PropSet="";
        for PropSet in cybcon_was.splitArray(cybcon_was.showAttribute(MQQCF, 'propertySet')):
          CusProp="";
          for CusProp in cybcon_was.splitArray(cybcon_was.showAttribute(PropSet, 'resourceProperties')):
            dataOut({'name': "resourceProperty", 'value': cybcon_was.showAttribute(CusProp, 'value'), 'description': cybcon_was.showAttribute(CusProp, 'name'), 'tagname': "property"});
          if CusProp == "":
            dataOut({'value': "No resource properties found in this property set."});
        if PropSet == "":
          dataOut({'value': " No property set found."});
        dataOut({'tagname': "customproperties", 'tagtype': "2"});

        dataOut({'description': "Connection pool properties", 'tagname': "connectionpool", 'tagtype': "1"});
        MQQCF_CPID = cybcon_was.showAttribute(MQQCF, 'connectionPool');
        if MQQCF_CPID != "":
          dataOut({'name': "connectionTimeout", 'value': cybcon_was.showAttribute(MQQCF_CPID, 'connectionTimeout'), 'unit': "seconds", 'description': "Connection timeout", 'tagname': "connectiontimeout"});
          dataOut({'name': "maxConnections", 'value': cybcon_was.showAttribute(MQQCF_CPID, 'maxConnections'), 'unit': "connections", 'description': "Maximum connections", 'tagname': "maxconnections"});
          dataOut({'name': "minConnections", 'value': cybcon_was.showAttribute(MQQCF_CPID, 'minConnections'), 'unit': "connections", 'description': "Minimum connections", 'tagname': "minconnections"});
          dataOut({'name': "reapTime", 'value': cybcon_was.showAttribute(MQQCF_CPID, 'reapTime'), 'unit': "seconds", 'description': "Reap time", 'tagname': "reaptime"});
          dataOut({'name': "unusedTimeout", 'value': cybcon_was.showAttribute(MQQCF_CPID, 'unusedTimeout'), 'unit': "seconds", 'description': "Unused timeout", 'tagname': "unusedtimeout"});
          dataOut({'name': "agedTimeout", 'value': cybcon_was.showAttribute(MQQCF_CPID, 'agedTimeout'), 'unit': "seconds", 'description': "Aged timeout", 'tagname': "agedtimeout"});
          dataOut({'name': "purgePolicy", 'value': cybcon_was.showAttribute(MQQCF_CPID, 'purgePolicy'), 'description': "Purge policy", 'tagname': "purgepolicy"});
        else:
          dataOut({'description': "WARNING", 'value': "No connection pool configuration object found - skip connection pool properties!"});
        dataOut({'tagname': "connectionpool", 'tagtype': "2"});
        dataOut({'description': "Session pools", 'tagname': "sessionpool", 'tagtype': "1"});
        MQQCF_SPID = cybcon_was.showAttribute(MQQCF, 'sessionPool');
        if MQQCF_SPID != "":
          dataOut({'name': "connectionTimeout", 'value': cybcon_was.showAttribute(MQQCF_SPID, 'connectionTimeout'), 'unit': "seconds", 'description': "Connection timeout", 'tagname': "connectiontimeout"});
          dataOut({'name': "maxConnections", 'value': cybcon_was.showAttribute(MQQCF_SPID, 'maxConnections'), 'unit': "connections", 'description': "Maximum connections", 'tagname': "maxconnections"});
          dataOut({'name': "minConnections", 'value': cybcon_was.showAttribute(MQQCF_SPID, 'minConnections'), 'unit': "connections", 'description': "Minimum connections", 'tagname': "minconnections"});
          dataOut({'name': "reapTime", 'value': cybcon_was.showAttribute(MQQCF_SPID, 'reapTime'), 'unit': "seconds", 'description': "Reap time", 'tagname': "reaptime"});
          dataOut({'name': "unusedTimeout", 'value': cybcon_was.showAttribute(MQQCF_SPID, 'unusedTimeout'), 'unit': "seconds", 'description': "Unused timeout", 'tagname': "unusedtimeout"});
          dataOut({'name': "agedTimeout", 'value': cybcon_was.showAttribute(MQQCF_SPID, 'agedTimeout'), 'unit': "seconds", 'description': "Aged timeout", 'tagname': "agedtimeout"});
          dataOut({'name': "purgePolicy", 'value': cybcon_was.showAttribute(MQQCF_SPID, 'purgePolicy'), 'description': "Purge policy", 'tagname': "purgepolicy"});
        else:
          dataOut({'description': "WARNING", 'value': "No session pool configuration object found - skip session pool properties!"});
        dataOut({'tagname': "sessionpool", 'tagtype': "2"});
        dataOut({'tagname': "mqqueueconnectionfactory", 'tagtype': "2"});
      else:
        dataOut({'value': "No WebSphere MQ queue connection factory defined on this scope."});
    dataOut({'tagname': "mqqueueconnectionfactories", 'tagtype': "2"});

    dataOut({'description': "WebSphere MQ queue destinations", 'tagname': "mqqueues", 'tagtype': "1"});
    for MQQDest in AdminConfig.list('MQQueue', JMSProviderID).split(lineSeparator):
      if MQQDest != "":
        dataOut({'tagname': "mqqueuedestination", 'tagtype': "1"});
        dataOut({'name': "name", 'value': cybcon_was.showAttribute(MQQDest, 'name'), 'description': "Name", 'tagname': "name"});
        dataOut({'name': "jndiName", 'value': cybcon_was.showAttribute(MQQDest, 'jndiName'), 'description': "JNDI name", 'tagname': "jndiname"});
        dataOut({'name': "baseQueueName", 'value': cybcon_was.showAttribute(MQQDest, 'baseQueueName'), 'description': "Queue name", 'tagname': "basequeuename"});
        dataOut({'name': 'baseQueueManagerName', 'value': cybcon_was.showAttribute(MQQDest, 'baseQueueManagerName'), 'description': 'Queue manager or Queue sharing group name', 'tagname': 'baseQueueManagerName'});
        dataOut({'description': 'Advanced properties', 'tagname': "advancedproperties", 'tagtype': "1"});
        dataOut({'name': 'persistence', 'value': cybcon_was.showAttribute(MQQDest, 'persistence'), 'description': 'Persistence', 'tagname': 'persistence'});
        dataOut({'name': 'priority', 'value': cybcon_was.showAttribute(MQQDest, 'priority'), 'description': 'Priority', 'tagname': 'priority'});
        dataOut({'name': 'specifiedPriority', 'value': cybcon_was.showAttribute(MQQDest, 'specifiedPriority'), 'description': 'Specified priority', 'tagname': 'specifiedPriority'});
        dataOut({'name': 'expiry', 'value': cybcon_was.showAttribute(MQQDest, 'expiry'), 'description': 'Expiry', 'tagname': 'expiry'});
        dataOut({'name': 'specifiedExpiry', 'value': cybcon_was.showAttribute(MQQDest, 'specifiedExpiry'), 'description': 'Specified expiry', 'tagname': 'specifiedExpiry'});
        dataOut({'name': 'CCSID', 'value': cybcon_was.showAttribute(MQQDest, 'CCSID'), 'description': 'Coded character set identifier (CCSID)', 'tagname': 'CCSID'});
        dataOut({'name': 'useNativeEncoding', 'value': cybcon_was.showAttribute(MQQDest, 'useNativeEncoding'), 'description': 'Use native encoding', 'tagname': 'useNativeEncoding'});
        dataOut({'name': 'integerEncoding', 'value': cybcon_was.showAttribute(MQQDest, 'integerEncoding'), 'description': 'Integer encoding', 'tagname': 'integerEncoding'});
        dataOut({'name': 'decimalEncoding', 'value': cybcon_was.showAttribute(MQQDest, 'decimalEncoding'), 'description': 'Decimal encoding', 'tagname': 'decimalEncoding'});
        dataOut({'name': 'floatingPointEncoding', 'value': cybcon_was.showAttribute(MQQDest, 'floatingPointEncoding'), 'description': 'Floating point encoding', 'tagname': 'floatingPointEncoding'});
        #dataOut({'name': 'useRFH2', 'value': cybcon_was.showAttribute(MQQDest, 'useRFH2'), 'description': 'Append RFH version 2 headers to messages sent to this destination', 'tagname': 'useRFH2'});
        dataOut({'name': 'targetClient', 'value': cybcon_was.showAttribute(MQQDest, 'targetClient'), 'description': 'Message body (Target client)', 'tagname': 'targetClient'});
        dataOut({'name': 'replyToStyle', 'value': cybcon_was.showAttribute(MQQDest, 'replyToStyle'), 'description': 'Reply to style', 'tagname': 'replyToStyle'});
        dataOut({'name': 'sendAsync', 'value': cybcon_was.showAttribute(MQQDest, 'sendAsync'), 'description': 'Asynchronously send messages to the queue manager', 'tagname': 'sendAsync'});
        dataOut({'name': 'readAhead', 'value': cybcon_was.showAttribute(MQQDest, 'readAhead'), 'description': 'Read ahead, and cache, non-persistent messages for consumers', 'tagname': 'readAhead'});
        dataOut({'name': 'readAheadClose', 'value': cybcon_was.showAttribute(MQQDest, 'readAheadClose'), 'description': 'Read ahead consumer close method', 'tagname': 'readAheadClose'});
        dataOut({'name': 'mqmdReadEnabled', 'value': cybcon_was.showAttribute(MQQDest, 'mqmdReadEnabled'), 'description': 'MQMD read enabled', 'tagname': 'mqmdReadEnabled'});
        dataOut({'name': 'mqmdWriteEnabled', 'value': cybcon_was.showAttribute(MQQDest, 'mqmdWriteEnabled'), 'description': 'MQMD write enabled', 'tagname': 'mqmdWriteEnabled'});
        dataOut({'name': 'mqmdMessageContext', 'value': cybcon_was.showAttribute(MQQDest, 'mqmdMessageContext'), 'description': 'MQMD message context', 'tagname': 'mqmdMessageContext'});
        dataOut({'tagname': "advancedproperties", 'tagtype': "2"});

        dataOut({'description': "WebSphere MQ Queue Connection Properties", 'tagname': "mqqueueconnectionproperties", 'tagtype': "1"});
        dataOut({'name': "queueManagerPort", 'value': cybcon_was.showAttribute(MQQDest, 'queueManagerPort'), 'description': "Queue manager port", 'tagname': "queueManagerPort"});
        dataOut({'name': "serverConnectionChannelName", 'value': cybcon_was.showAttribute(MQQDest, 'serverConnectionChannelName'), 'description': "Server connection channel name", 'tagname': "serverConnectionChannelName"});
        dataOut({'name': "userName", 'value': cybcon_was.showAttribute(MQQDest, 'userName'), 'description': "User ID", 'tagname': "userName"});
        dataOut({'tagname': "mqqueueconnectionproperties", 'tagtype': "2"});
        dataOut({'tagname': "mqqueuedestination", 'tagtype': "2"});
      else:
        dataOut({'value': "No WebSphere MQ queue destination defined on this scope."});
    dataOut({'tagname': "mqqueues", 'tagtype': "2"});
  else:
    dataOut({'value': "No WebSphere MQ JMS Provider defined on this scope."});

  dataOut({'tagname': "webspheremq", 'tagtype': "2"});
  dataOut({'tagname': "jmsproviders", 'tagtype': "2"});

#----------------------------------------------------------------------------
# get_JDBCProviderProperties
#   description: search the JDBC provider properties and its dependend
#     datasources by it's given objectID
#   input: objectID (can be cellID, clusterID, nodeID or serverID)
#   output: informations on stdout
#   return: -
#----------------------------------------------------------------------------
def get_JDBCProviderProperties(objectID):
  dataOut({'description': "JDBC Providers", 'tagname': "jdbcproviders", 'tagtype': "1"});
# get name and objectType of the objectID
  objectName = cybcon_was.showAttribute(objectID, 'name');
  objectType = cybcon_was.get_ObjectTypeByID(objectID);
  if objectType == "Server":
    nodeName = cybcon_was.get_nodeNameByServerID(objectID);
    if nodeName != "": objectType = 'Node:' + nodeName + '/' + objectType;
# get IDs, searching by scope, and type
  for JDBCProvider in AdminConfig.getid('/' + objectType + ':' + objectName + '/JDBCProvider:/').split(lineSeparator):
    if JDBCProvider != "":
      dataOut({'tagname': "jdbcprovider", 'tagtype': "1"});
      dataOut({'name': "name", 'value': cybcon_was.showAttribute(JDBCProvider, 'name'), 'description': "Name", 'tagname': "name"});
      dataOut({'name': "description", 'value': cybcon_was.showAttribute(JDBCProvider, 'description'), 'description': "Description", 'tagname': "description"});
      dataOut({'name': "classpath", 'value': cybcon_was.showAttribute(JDBCProvider, 'classpath'), 'description': "Class path", 'tagname': "classpath"});
      dataOut({'name': "nativepath", 'value': cybcon_was.showAttribute(JDBCProvider, 'nativepath'), 'description': "Native library path", 'tagname': "nativepath"});
      dataOut({'name': "implementationClassName", 'value': cybcon_was.showAttribute(JDBCProvider, 'implementationClassName'), 'description': "Implementation class name", 'tagname': "implementationclassname"});
      dataOut({'name': "providerType", 'value': cybcon_was.showAttribute(JDBCProvider, 'providerType'), 'description': "Provider type", 'tagname': "providerType"});
      dataOut({'name': "xa", 'value': cybcon_was.showAttribute(JDBCProvider, 'xa'), 'description': "XA", 'tagname': "xa"});
      dataOut({'description': "Data sources", 'tagname': "datasources", 'tagtype': "1"});
      for DataSource in AdminConfig.list('DataSource', JDBCProvider).split(lineSeparator):
        if DataSource != "":
          dataOut({'tagname': "datasource", 'tagtype': "1"});
          dataOut({'name': "name", 'value': cybcon_was.showAttribute(DataSource, 'name'), 'description': "Name", 'tagname': "name"});
          dataOut({'name': "jndiName", 'value': cybcon_was.showAttribute(DataSource, 'jndiName'), 'description': "JNDI name", 'tagname': "jndiName"});
          dataOut({'name': "description", 'value': cybcon_was.showAttribute(DataSource, 'description'), 'description': "Description", 'tagname': "description"});
          dataOut({'name': "datasourceHelperClassname", 'value': cybcon_was.showAttribute(DataSource, 'datasourceHelperClassname'), 'description': "Data store helper class", 'tagname': "datasourcehelperclassname"});
          dataOut({'name': "authDataAlias", 'value': cybcon_was.showAttribute(DataSource, 'authDataAlias'), 'description': "Component-managed authentication alias", 'tagname': "authDataAlias"});
          dataOut({'name': "xaRecoveryAuthAlias", 'value': cybcon_was.showAttribute(DataSource, 'xaRecoveryAuthAlias'), 'description': "Authentication alias for XA recovery", 'tagname': "xarecoveryauthalias"});
          dataOut({'description': "Connection pool properties", 'tagname': "connectionpoolproperties", 'tagtype': "1"});
          DataSourceCP = cybcon_was.showAttribute(DataSource, 'connectionPool');
          if DataSourceCP != "":
            dataOut({'name': "connectionTimeout", 'value': cybcon_was.showAttribute(DataSourceCP, 'connectionTimeout'), 'unit': "seconds", 'description': "Connection timeout", 'tagname': "connectiontimeout"});
            dataOut({'name': "maxConnections", 'value': cybcon_was.showAttribute(DataSourceCP, 'maxConnections'), 'unit': "connections", 'description': "Maximum connections", 'tagname': "maxconnections"});
            dataOut({'name': "minConnections", 'value': cybcon_was.showAttribute(DataSourceCP, 'minConnections'), 'unit': "connections", 'description': "Minimum connections", 'tagname': "minconnections"});
            dataOut({'name': "reapTime", 'value': cybcon_was.showAttribute(DataSourceCP, 'reapTime'), 'unit': "seconds", 'description': "Reap time", 'tagname': "reaptime"});
            dataOut({'name': "unusedTimeout", 'value': cybcon_was.showAttribute(DataSourceCP, 'unusedTimeout'), 'unit': "seconds", 'description': "Unused timeout", 'tagname': "unusedtimeout"});
            dataOut({'name': "agedTimeout", 'value': cybcon_was.showAttribute(DataSourceCP, 'agedTimeout'), 'unit': "seconds", 'description': "Aged timeout", 'tagname': "agedtimeout"});
            dataOut({'name': "purgePolicy", 'value': cybcon_was.showAttribute(DataSourceCP, 'apurgePolicy'), 'description': "Purge policy", 'tagname': "purgePolicy"});
            dataOut({'description': "Advanced connection pool properties", 'tagname': "advancedconnectionpoolproperties", 'tagtype': "1"});
            dataOut({'name': "numberOfSharedPoolPartitions", 'value': cybcon_was.showAttribute(DataSourceCP, 'numberOfSharedPoolPartitions'), 'description': "Number of shared partitions", 'tagname': "numberOfSharedPoolPartitions"});
            dataOut({'name': "numberOfFreePoolPartitions", 'value': cybcon_was.showAttribute(DataSourceCP, 'numberOfFreePoolPartitions'), 'description': "Number of free pool partitions", 'tagname': "numberOfFreePoolPartitions"});
            dataOut({'name': "freePoolDistributionTableSize", 'value': cybcon_was.showAttribute(DataSourceCP, 'freePoolDistributionTableSize'), 'description': "Free pool distribution table size", 'tagname': "freePoolDistributionTableSize"});
            dataOut({'name': "surgeThreshold", 'value': cybcon_was.showAttribute(DataSourceCP, 'surgeThreshold'), 'unit': "connections", 'description': "Surge threshold", 'tagname': "surgeThreshold"});
            dataOut({'name': "surgeCreationInterval", 'value': cybcon_was.showAttribute(DataSourceCP, 'surgeCreationInterval'), 'unit': "seconds", 'description': "Surge creation interval", 'tagname': "surgeCreationInterval"});
            dataOut({'name': "surgeCreationInterval", 'value': cybcon_was.showAttribute(DataSourceCP, 'surgeCreationInterval'), 'unit': "seconds", 'description': "Surge creation interval", 'tagname': "surgeCreationInterval"});
            dataOut({'name': "stuckTimerTime", 'value': cybcon_was.showAttribute(DataSourceCP, 'stuckTimerTime'), 'unit': "seconds", 'description': "Stuck timer time", 'tagname': "stuckTimerTime"});
            dataOut({'name': "stuckTime", 'value': cybcon_was.showAttribute(DataSourceCP, 'stuckTime'), 'unit': "seconds", 'description': "Stuck time", 'tagname': "stuckTime"});
            dataOut({'name': "stuckThreshold", 'value': cybcon_was.showAttribute(DataSourceCP, 'stuckThreshold'), 'unit': "connections", 'description': "Stuck threshold", 'tagname': "stuckThreshold"});
            dataOut({'tagname': "advancedconnectionpoolproperties", 'tagtype': "2"});
          else:
            dataOut({'value': "No connection pool properties found for this datasource - skip properties!"});
          dataOut({'tagname': "connectionpoolproperties", 'tagtype': "2"});

          dataOut({'description': "WebSphere Application Server data source properties", 'tagname': "wasdatasourceproperties", 'tagtype': "1"});
          dataOut({'name': "statementCacheSize", 'value': cybcon_was.showAttribute(DataSource, 'statementCacheSize'), 'unit': "statements", 'description': "Statement cache size", 'tagname': "statementcachesize"});
          dataOut({'name': "manageCachedHandles", 'value': cybcon_was.showAttribute(DataSource, 'manageCachedHandles'), 'description': "Manage cached handles", 'tagname': "managecachedhandles"});
          dataOut({'name': "logMissingTransactionContext", 'value': cybcon_was.showAttribute(DataSource, 'logMissingTransactionContext'), 'description': "Log missing transaction context", 'tagname': "logmissingtransactioncontext"});
          dataOut({'description': "Property set", 'tagname': "customproperties", 'tagtype': "1"});
          PropSet="";
          for PropSet in cybcon_was.splitArray(cybcon_was.showAttribute(DataSource, 'propertySet')):
            CusProp="";
            for CusProp in cybcon_was.splitArray(cybcon_was.showAttribute(PropSet, 'resourceProperties')):
              dataOut({'name': "resourceProperty", 'value': cybcon_was.showAttribute(CusProp, 'value'), 'description': cybcon_was.showAttribute(CusProp, 'name'), 'tagname': "property"});
            if CusProp == "":
              dataOut({'value': "No resource properties found in this property set."});
          if PropSet == "":
            dataOut({'value': " No property set found."});
          dataOut({'tagname': "customproperties", 'tagtype': "2"});
          dataOut({'tagname': "wasdatasourceproperties", 'tagtype': "2"});
          dataOut({'tagname': "datasource", 'tagtype': "2"});
        else:
          dataOut({'value': "No Data source defined for this provider."});
      dataOut({'tagname': "datasources", 'tagtype': "2"});
      dataOut({'tagname': "jdbcprovider", 'tagtype': "2"});
    else:
      dataOut({'value': "No JDBC provider defined on this scope."});
  dataOut({'tagname': "jdbcproviders", 'tagtype': "2"});

#----------------------------------------------------------------------------
# get_ResourceAdapterProperties
#   description: search the Resource Adapter properties and its dependend
#     connection factories by it's given objectID
#   input: objectID (can be cellID, clusterID, nodeID or serverID)
#   output: informations on stdout
#   return: -
#----------------------------------------------------------------------------
def get_ResourceAdapterProperties(objectID):
  dataOut({'description': "Resource Adapters", 'tagname': "resourceadapters", 'tagtype': "1"});
# get name and objectType of the objectID
  objectName = cybcon_was.showAttribute(objectID, 'name');
  objectType = cybcon_was.get_ObjectTypeByID(objectID);
  if objectType == "Server":
    nodeName = cybcon_was.get_nodeNameByServerID(objectID);
    if nodeName != "": objectType = 'Node:' + nodeName + '/' + objectType;
# get IDs, searching by scope, and type
  for RA in AdminConfig.getid('/' + objectType + ':' + objectName + '/J2CResourceAdapter:/').split(lineSeparator):
    if RA != "":
      dataOut({'tagname': "resourceadapter", 'tagtype': "1"});
      dataOut({'name': "name", 'value': cybcon_was.showAttribute(RA, 'name'), 'description': "Name", 'tagname': "name"});
      dataOut({'name': "description", 'value': cybcon_was.showAttribute(RA, 'description'), 'description': "Description", 'tagname': "description"});
      dataOut({'name': "classpath", 'value': cybcon_was.showAttribute(RA, 'classpath'), 'description': "Class path", 'tagname': "classpath"});
      dataOut({'description': "J2C connection factories", 'tagname': "j2cconnectionfactories", 'tagtype': "1"});
      for RACF in AdminConfig.list('J2CConnectionFactory', RA).split(lineSeparator):
        if RACF != "":
          dataOut({'tagname': "j2cconnectionfactory", 'tagtype': "1"});
          dataOut({'name': "name", 'value': cybcon_was.showAttribute(RACF, 'name'), 'description': "Name", 'tagname': "name"});
          dataOut({'name': "description", 'value': cybcon_was.showAttribute(RACF, 'description'), 'description': "Description", 'tagname': "description"});
          dataOut({'name': "jndiName", 'value': cybcon_was.showAttribute(RACF, 'jndiName'), 'description': "JNDI name", 'tagname': "jndiName"});
          mappingID = cybcon_was.showAttribute(RACF, 'mapping');
          if mappingID != "": dataOut({'name': "authDataAlias", 'value': cybcon_was.showAttribute(mappingID, 'authDataAlias'), 'description': "Container-managed authentication alias", 'tagname': "authdataalias"});
          dataOut({'description': "Connection pool properties", 'tagname': "connectionpoolproperties", 'tagtype': "1"});
          RACF_CPID = cybcon_was.showAttribute(RACF, 'connectionPool');
          if RACF_CPID != "":
            dataOut({'name': "connectionTimeout", 'value': cybcon_was.showAttribute(RACF_CPID, 'connectionTimeout'), 'unit': "seconds", 'description': "Connection timeout", 'tagname': "connectiontimeout"});
            dataOut({'name': "maxConnections", 'value': cybcon_was.showAttribute(RACF_CPID, 'maxConnections'), 'unit': "connections", 'description': "Maximum connections", 'tagname': "maxconnections"});
            dataOut({'name': "minConnections", 'value': cybcon_was.showAttribute(RACF_CPID, 'minConnections'), 'unit': "connections", 'description': "Minimum connections", 'tagname': "minconnections"});
            dataOut({'name': "reapTime", 'value': cybcon_was.showAttribute(RACF_CPID, 'reapTime'), 'unit': "seconds", 'description': "Reap time", 'tagname': "reaptime"});
            dataOut({'name': "unusedTimeout", 'value': cybcon_was.showAttribute(RACF_CPID, 'unusedTimeout'), 'unit': "seconds", 'description': "Unused timeout", 'tagname': "unusedtimeout"});
            dataOut({'name': "agedTimeout", 'value': cybcon_was.showAttribute(RACF_CPID, 'agedTimeout'), 'unit': "seconds", 'description': "Aged timeout", 'tagname': "agedtimeout"});
            dataOut({'name': "purgePolicy", 'value': cybcon_was.showAttribute(RACF_CPID, 'purgePolicy'), 'description': "Purge policy", 'tagname': "purgepolicy"});
          else:
            dataOut({'description': "WARNING", 'value': "No connection pool configuration object found - skip connection pool properties!"});
          dataOut({'tagname': "connectionpoolproperties", 'tagtype': "2"});
          dataOut({'description': "Custom properties", 'tagname': "customproperties", 'tagtype': "1"});
          PropSet="";
          for PropSet in cybcon_was.splitArray(cybcon_was.showAttribute(RACF, 'propertySet')):
            CusProp="";
            for CusProp in cybcon_was.splitArray(cybcon_was.showAttribute(PropSet, 'resourceProperties')):
              dataOut({'name': "resourceProperty", 'value': cybcon_was.showAttribute(CusProp, 'value'), 'description': cybcon_was.showAttribute(CusProp, 'name'), 'tagname': "property"});
            if CusProp == "":
              dataOut({'value': "No resource properties found in this property set."});
          if PropSet == "":
            dataOut({'value': " No property set found."});
          dataOut({'tagname': "customproperties", 'tagtype': "2"});
          dataOut({'tagname': "j2cconnectionfactory", 'tagtype': "2"});
        else:
          dataOut({'value': "No J2C connection factory defined for this resource adapter."});
      dataOut({'tagname': "j2cconnectionfactories", 'tagtype': "2"});
      dataOut({'tagname': "resourceadapter", 'tagtype': "2"});
    else:
      dataOut({'value': "No resource adapter defined on this scope."});

  dataOut({'description': "J2C Activation specifications", 'tagname': "j2cactivationspecs", 'tagtype': "1"});
  for J2CAcSpecID in AdminConfig.list('J2CActivationSpec', objectID).split(lineSeparator):
    if J2CAcSpecID != "":
      dataOut({'tagname': "j2cactivationspec", 'tagtype': "1"});
      dataOut({'name': "name", 'value': cybcon_was.showAttribute(J2CAcSpecID, 'name'), 'description': "Name", 'tagname': "name"});
      dataOut({'name': "jndiName", 'value': cybcon_was.showAttribute(J2CAcSpecID, 'jndiName'), 'description': "JNDI name", 'tagname': "jndiName"});
      dataOut({'name': "description", 'value': cybcon_was.showAttribute(J2CAcSpecID, 'description'), 'description': "Description", 'tagname': "description"});
      dataOut({'description': "Custom properties", 'tagname': "customproperties", 'tagtype': "1"});
      CusProp="";
      for CusProp in cybcon_was.splitArray(cybcon_was.showAttribute(J2CAcSpecID, 'resourceProperties')):
        dataOut({'name': "resourceProperty", 'value': cybcon_was.showAttribute(CusProp, 'value'), 'description': cybcon_was.showAttribute(CusProp, 'name'), 'tagname': "property"});
        if CusProp == "":
          dataOut({'value': "No custom properties configured for this J2C Activation specification!"});
      dataOut({'tagname': "customproperties", 'tagtype': "2"});
      dataOut({'tagname': "j2cactivationspec", 'tagtype': "2"});
    else:
      dataOut({'value': "No J2C Activation specifications defined on this level."});
  dataOut({'tagname': "j2cactivationspecs", 'tagtype': "2"});
  dataOut({'tagname': "resourceadapters", 'tagtype': "2"});

#----------------------------------------------------------------------------
# get_URLProviderProperties
#   description: search the URL provider properties by it's given objectID
#   input: objectID (can be cellID, clusterID, nodeID or serverID)
#   output: informations on stdout
#   return: -
#----------------------------------------------------------------------------
def get_URLProviderProperties(objectID):
  dataOut({'description': "URL Providers", 'tagname': "urlproviders", 'tagtype': "1"});
# get name and objectType of the objectID
  objectName = cybcon_was.showAttribute(objectID, 'name');
  objectType = cybcon_was.get_ObjectTypeByID(objectID);
  if objectType == "Server":
    nodeName = cybcon_was.get_nodeNameByServerID(objectID);
    if nodeName != "": objectType = 'Node:' + nodeName + '/' + objectType;
# get IDs, searching by scope, and type
  for URLproviderID in AdminConfig.getid('/' + objectType + ':' + objectName + '/URLProvider:/').split(lineSeparator):
    if URLproviderID != "":
      dataOut({'tagname': "urlprovider", 'tagtype': "1"});
      dataOut({'name': "name", 'value': cybcon_was.showAttribute(URLproviderID, 'name'), 'description': "Name", 'tagname': "name"});
      dataOut({'name': "description", 'value': cybcon_was.showAttribute(URLproviderID, 'description'), 'description': "Description", 'tagname': "description"});
      dataOut({'name': "classpath", 'value': cybcon_was.showAttribute(URLproviderID, 'classpath'), 'description': "Class path", 'tagname': "classpath"});
      dataOut({'name': "streamHandlerClassName", 'value': cybcon_was.showAttribute(URLproviderID, 'streamHandlerClassName'), 'description': "Stream handler class name", 'tagname': "streamhandlerclassname"});
      dataOut({'name': "protocol", 'value': cybcon_was.showAttribute(URLproviderID, 'protocol'), 'description': "Protocol", 'tagname': "protocol"});
      dataOut({'description': "URLs", 'tagname': "urls", 'tagtype': "1"});
      for URL in AdminConfig.list('URL', URLproviderID).split(lineSeparator):
        if URL != "":
          dataOut({'tagname': "url", 'tagtype': "1"});
          dataOut({'name': "name", 'value': cybcon_was.showAttribute(URL, 'name'), 'description': "Name", 'tagname': "name"});
          dataOut({'name': "jndiName", 'value': cybcon_was.showAttribute(URL, 'jndiName'), 'description': "JNDI name", 'tagname': "jndiName"});
          dataOut({'name': "description", 'value': cybcon_was.showAttribute(URL, 'description'), 'description': "Description", 'tagname': "description"});
          dataOut({'name': "spec", 'value': cybcon_was.showAttribute(URL, 'spec'), 'description': "Specification", 'tagname': "spec"});
          dataOut({'tagname': "url", 'tagtype': "2"});
        else:
          dataOut({'value': "No URLs defined for this URL provider."});
      dataOut({'tagname': "urls", 'tagtype': "2"});
      dataOut({'tagname': "urlprovider", 'tagtype': "2"});
    else:
      dataOut({'value': "No URL provider defined on this scope."});
  dataOut({'tagname': "urlproviders", 'tagtype': "2"});


#----------------------------------------------------------------------------
# get_ResourceEnvironmentProperties
#   description: search the resource env. properties by it's given objectID
#   input: objectID (can be cellID, clusterID, nodeID or serverID)
#   output: informations on stdout
#   return: -
#----------------------------------------------------------------------------
def get_ResourceEnvironmentProperties(objectID):
  dataOut({'description': "Resource Environment", 'tagname': "resourceenvironment", 'tagtype': "1"});
# get name and objectType of the objectID
  objectName = cybcon_was.showAttribute(objectID, 'name');
  objectType = cybcon_was.get_ObjectTypeByID(objectID);
  if objectType == "Server":
    nodeName = cybcon_was.get_nodeNameByServerID(objectID);
    if nodeName != "": objectType = 'Node:' + nodeName + '/' + objectType;

  dataOut({'description': "Resource Environment Providers", 'tagname': "resourceenvironmentproviders", 'tagtype': "1"});
  for ResEnvProvID in AdminConfig.getid('/' + objectType + ':' + objectName + '/ResourceEnvironmentProvider:/').split(lineSeparator):
    if ResEnvProvID != "":
      dataOut({'tagname': "resourceenvironmentprovider", 'tagtype': "1"});
      dataOut({'name': "name", 'value': cybcon_was.showAttribute(ResEnvProvID, 'name'), 'description': "Name", 'tagname': "name"});
      dataOut({'name': "description", 'value': cybcon_was.showAttribute(ResEnvProvID, 'description'), 'description': "Description", 'tagname': "description"});
      dataOut({'description': "Referenceables", 'tagname': "referenceables", 'tagtype': "1"});
      ReferenceablesID="";
      for ReferenceablesID in cybcon_was.splitArray(cybcon_was.showAttribute(ResEnvProvID, 'referenceables')):
        dataOut({'tagname': "referenceable", 'tagtype': "1"});
        dataOut({'name': "factoryClassname", 'value': cybcon_was.showAttribute(ReferenceablesID, 'factoryClassname'), 'description': "Factory class name", 'tagname': "factoryclassname"});
        dataOut({'name': "classname", 'value': cybcon_was.showAttribute(ReferenceablesID, 'classname'), 'description': "Class name", 'tagname': "classname"});
        dataOut({'tagname': "referenceable", 'tagtype': "2"});
      if ReferenceablesID == "":
        dataOut({'value': "No Referenceables found for this Resource Environment Provider."});
      dataOut({'tagname': "referenceables", 'tagtype': "2"});

      dataOut({'description': "Resource environment entries", 'tagname': "resourceenvironmententries", 'tagtype': "1"});
      for ResEnvEntryID in AdminConfig.list('ResourceEnvEntry', ResEnvProvID).split(lineSeparator):
        if ResEnvEntryID != "":
          dataOut({'tagname': "resourceenvironmententry", 'tagtype': "1"});
          dataOut({'name': "name", 'value': cybcon_was.showAttribute(ResEnvEntryID, 'name'), 'description': "Name", 'tagname': "name"});
          dataOut({'name': "jndiName", 'value': cybcon_was.showAttribute(ResEnvEntryID, 'jndiName'), 'description': "JNDI name", 'tagname': "jndiname"});
          dataOut({'name': "description", 'value': cybcon_was.showAttribute(ResEnvEntryID, 'description'), 'description': "Description", 'tagname': "description"});
          dataOut({'name': "referenceable", 'value': cybcon_was.showAttribute(cybcon_was.showAttribute(ResEnvEntryID, 'referenceable'), 'factoryClassname'), 'description': "Referenceables", 'tagname': "referenceable"});
          dataOut({'description': "Custom properties", 'tagname': "customproperties", 'tagtype': "1"});
          PropSet="";
          for PropSet in cybcon_was.splitArray(cybcon_was.showAttribute(ResEnvEntryID, 'propertySet')):
            CusProp="";
            for CusProp in cybcon_was.splitArray(cybcon_was.showAttribute(PropSet, 'resourceProperties')):
              dataOut({'name': "resourceProperty", 'value': cybcon_was.showAttribute(CusProp, 'value'), 'description': cybcon_was.showAttribute(CusProp, 'name'), 'tagname': "property"});
            if CusProp == "":
              dataOut({'value': "No resource properties found in this property set."});
          if PropSet == "":
            dataOut({'value': " No property set found."});
          dataOut({'tagname': "customproperties", 'tagtype': "2"});
          dataOut({'tagname': "resourceenvironmententry", 'tagtype': "2"});
        else:
          dataOut({'value': "No Resource environment entry found for this Resource Environment Provider."});
      dataOut({'tagname': "resourceenvironmententries", 'tagtype': "2"});

      dataOut({'description': "Custom properties", 'tagname': "customproperties", 'tagtype': "1"});
      PropSet="";
      for PropSet in cybcon_was.splitArray(cybcon_was.showAttribute(ResEnvProvID, 'propertySet')):
        CusProp="";
        for CusProp in cybcon_was.splitArray(cybcon_was.showAttribute(PropSet, 'resourceProperties')):
          dataOut({'name': "resourceProperty", 'value': cybcon_was.showAttribute(CusProp, 'value'), 'description': cybcon_was.showAttribute(CusProp, 'name'), 'tagname': "property"});
        if CusProp == "":
          dataOut({'value': "No resource properties found in this property set."});
      if PropSet == "":
        dataOut({'value': " No property set found."});
      dataOut({'tagname': "customproperties", 'tagtype': "2"});

      dataOut({'tagname': "resourceenvironmentprovider", 'tagtype': "2"});
    else:
      dataOut({'value': "No Resource Environment Providers found on this scope."});
  dataOut({'tagname': "resourceenvironmentproviders", 'tagtype': "2"});
  dataOut({'tagname': "resourceenvironment", 'tagtype': "2"});

#----------------------------------------------------------------------------
# get_MailProviderProperties
#   description: search the Mail provider properties by it's given objectID
#   input: objectID (can be cellID, clusterID, nodeID or serverID)
#   output: informations on stdout
#   return: -
#----------------------------------------------------------------------------
def get_MailProviderProperties(objectID):
  dataOut({'description': "Mail Providers", 'tagname': "mailproviders", 'tagtype': "1"});
# get name and objectType of the objectID
  objectName = cybcon_was.showAttribute(objectID, 'name');
  objectType = cybcon_was.get_ObjectTypeByID(objectID);
  if objectType == "Server":
    nodeName = cybcon_was.get_nodeNameByServerID(objectID);
    if nodeName != "": objectType = 'Node:' + nodeName + '/' + objectType;
# get IDs, searching by scope, and type
  for MailproviderID in AdminConfig.getid('/' + objectType + ':' + objectName + '/MailProvider:/').split(lineSeparator):
    if MailproviderID != "":
      dataOut({'tagname': "mailprovider", 'tagtype': "1"});
      dataOut({'name': "name", 'value': cybcon_was.showAttribute(MailproviderID, 'name'), 'description': "Name", 'tagname': "name"});
      dataOut({'name': "description", 'value': cybcon_was.showAttribute(MailproviderID, 'description'), 'description': "Description", 'tagname': "description"});
      dataOut({'description': "Mail sessions", 'tagname': "mailsessions", 'tagtype': "1"});
      for MailSession in AdminConfig.list('MailSession', MailproviderID).split(lineSeparator):
        if MailSession != "":
          dataOut({'tagname': "mailsession", 'tagtype': "1"});
          dataOut({'name': "name", 'value': cybcon_was.showAttribute(MailSession, 'name'), 'description': "Name", 'tagname': "name"});
          dataOut({'name': "jndiName", 'value': cybcon_was.showAttribute(MailSession, 'jndiName'), 'description': "JNDI name", 'tagname': "jndiName"});
          dataOut({'name': "description", 'value': cybcon_was.showAttribute(MailSession, 'description'), 'description': "Description", 'tagname': "description"});
          dataOut({'name': "mailTransportHost", 'value': cybcon_was.showAttribute(MailSession, 'mailTransportHost'), 'description': "Mail transport host", 'tagname': "mailtransporthost"});
          dataOut({'name': "mailTransportProtocol", 'value': cybcon_was.showAttribute(MailSession, 'mailTransportProtocol'), 'description': "Mail transport protocol", 'tagname': "mailtransportprotocol"});
          dataOut({'name': "strict", 'value': cybcon_was.showAttribute(MailSession, 'strict'), 'description': "Enable strict Internet address parsing", 'tagname': "strict"});
          dataOut({'name': "mailFrom", 'value': cybcon_was.showAttribute(MailSession, 'mailFrom'), 'description': "Mail from", 'tagname': "mailfrom"});
          dataOut({'tagname': "mailsession", 'tagtype': "2"});
        else:
          dataOut({'value': "No mail session defined for this Mail provider."});
      dataOut({'tagname': "mailsessions", 'tagtype': "2"});
      dataOut({'tagname': "mailprovider", 'tagtype': "2"});
    else:
      dataOut({'value': "No Mail provider defined on this scope."});
  dataOut({'tagname': "mailproviders", 'tagtype': "2"});

#----------------------------------------------------------------------------
# get_securityProperties
#   description: output the security relevant informations
#   input: cellName
#   output: informations on stdout
#   return: -
#----------------------------------------------------------------------------
def get_securityProperties(cellName):
  securityID = AdminConfig.getid('/Cell:' + cellName + '/Security:/');
  dataOut({'description': "Security", 'tagname': "security", 'tagtype': "1"});
  dataOut({'description': "Global Security", 'tagname': "globalsecurity", 'tagtype': "1"});
  dataOut({'description': "General Properties", 'tagname': "generalproperties", 'tagtype': "1"});
  dataOut({'name': "enabled", 'value': cybcon_was.showAttribute(securityID, 'enabled'), 'description': "Enable global security", 'tagname': "enabled"});
  dataOut({'name': "appEnabled", 'value': cybcon_was.showAttribute(securityID, 'appEnabled'), 'description': "Enable application security", 'tagname': "appenabled"});
  dataOut({'name': "enforceJava2Security", 'value': cybcon_was.showAttribute(securityID, 'enforceJava2Security'), 'description': "Enable Java 2 security", 'tagname': "enforcejava2security"});
  dataOut({'name': "cacheTimeout", 'value': cybcon_was.showAttribute(securityID, 'cacheTimeout'), 'description': "Cache timeout", 'tagname': "cachetimeout"});
  dataOut({'name': "useDomainQualifiedUserNames", 'value': cybcon_was.showAttribute(securityID, 'useDomainQualifiedUserNames'), 'description': "Use domain-qualified user names", 'tagname': "useDomainQualifiedUserNames"});
  dataOut({'tagname': "generalproperties", 'tagtype': "2"});
  dataOut({'decription': 'Custom properties', 'tagname': "customproperties", 'tagtype': "1"});
  CusProp="";
  for CusProp in cybcon_was.splitArray(cybcon_was.showAttribute(securityID, 'properties')):
    dataOut({'name': "customProperty", 'value': cybcon_was.showAttribute(CusProp, 'value'), 'description': cybcon_was.showAttribute(CusProp, 'name'), 'tagname': "property"});
  if CusProp == "":
    dataOut({'value': "No custom properties set."});
  dataOut({'tagname': "customproperties", 'tagtype': "2"});
  dataOut({'tagname': "globalsecurity", 'tagtype': "2"});

  dataOut({'description': "User registries", 'tagname': "userregistries", 'tagtype': "1"});
  dataOut({'description': "Custom", 'tagname': "custom", 'tagtype': "1"});
  cusUserRegID=AdminConfig.list('CustomUserRegistry', securityID);
  dataOut({'name': 'primaryAdminId', 'value': cybcon_was.showAttribute(cusUserRegID, 'primaryAdminId'), 'description': 'Primary administrative user name', 'tagname': 'primaryAdminId'});
  useRegistryServerId=cybcon_was.showAttribute(cusUserRegID, 'useRegistryServerId');
  dataOut({'name': 'useRegistryServerId', 'value': useRegistryServerId, 'description': 'Use registry server ID', 'tagname': 'useRegistryServerId'});
  if useRegistryServerId == 'true':
    dataOut({'name': 'useRegistryServerIdSelect1', 'value': 'unset', 'description': 'Automatically generated server identity', 'tagname': 'useRegistryServerIdSelect1'});
    dataOut({'name': 'useRegistryServerIdSelect2', 'value': 'set', 'description': 'Server identity that is stored in the repository', 'tagname': 'useRegistryServerIdSelect2'});
    dataOut({'name': 'serverId', 'value': cybcon_was.showAttribute(cusUserRegID, 'serverId'), 'description': 'Server user ID or administrative user on a Version 6.0.x node', 'tagname': 'serverId'});
    dataOut({'name': 'serverPassword', 'value': cybcon_was.showAttribute(cusUserRegID, 'serverPassword'), 'description': 'Password', 'tagname': 'serverPassword'});
  else:
    dataOut({'name': 'useRegistryServerIdSelect1', 'value': 'set', 'description': 'Automatically generated server identity', 'tagname': 'useRegistryServerIdSelect1'});
    dataOut({'name': 'useRegistryServerIdSelect2', 'value': 'unset', 'description': 'Server identity that is stored in the repository', 'tagname': 'useRegistryServerIdSelect2'});
  dataOut({'name': 'customRegistryClassName', 'value': cybcon_was.showAttribute(cusUserRegID, 'customRegistryClassName'), 'description': 'Custom registry class name', 'tagname': 'customRegistryClassName'});
  dataOut({'name': 'ignoreCase', 'value': cybcon_was.showAttribute(cusUserRegID, 'ignoreCase'), 'description': 'Ignore case for authorization', 'tagname': 'ignoreCase'});
  dataOut({'description': "Custom properties", 'tagname': "customproperties", 'tagtype': "1"});
  CusProp="";
  for CusProp in cybcon_was.splitArray(cybcon_was.showAttribute(cusUserRegID, 'properties')):
    dataOut({'name': "customProperty", 'value': cybcon_was.showAttribute(CusProp, 'value'), 'description': cybcon_was.showAttribute(CusProp, 'name'), 'tagname': "property"});
  if CusProp == "":
    dataOut({'value': "No custom properties set."});
  dataOut({'tagname': "customproperties", 'tagtype': "2"});
  dataOut({'tagname': "custom", 'tagtype': "2"});
  dataOut({'tagname': "userregistries", 'tagtype': "2"});

  dataOut({'description': "Authentication", 'tagname': "authentication", 'tagtype': "1"});
  dataOut({'description': "Authentication mechanisms", 'tagname': "authenticationmechanisms", 'tagtype': "1"});
  dataOut({'description': "LTPA", 'tagname': "ltpa", 'tagtype': "1"});
  LTPAID = AdminConfig.list('LTPA', securityID);
  dataOut({'name': "timeout", 'value': cybcon_was.showAttribute(LTPAID, 'timeout'), 'description': "Timeout", 'tagname': "timeout"});
  dataOut({'description': "Trust association", 'tagname': "trustassociation", 'tagtype': "1"});
  TrusAssocID = cybcon_was.showAttribute(LTPAID, 'trustAssociation');
  if TrusAssocID != "":
    dataOut({'name': "enabled", 'value': cybcon_was.showAttribute(TrusAssocID, 'enabled'), 'description': "Enable trust association", 'tagname': "enabled"});
    dataOut({'description': "Interceptors", 'tagname': "interceptors", 'tagtype': "1"});
    for iceptID in cybcon_was.showAttribute(TrusAssocID, 'interceptors').split():
      iceptID = iceptID.replace("[", "").replace("]", "");
      if iceptID != "":
        dataOut({'tagname': "interceptor", 'tagtype': "1"});
        dataOut({'name': "interceptorClassName", 'value': cybcon_was.showAttribute(iceptID, 'interceptorClassName'), 'description': "Interceptor class name", 'tagname': "interceptorclassname"});

        dataOut({'description': "Custom properties", 'tagname': "customproperties", 'tagtype': "1"});
        CusProp="";
        for CusProp in cybcon_was.splitArray(cybcon_was.showAttribute(iceptID, 'trustProperties')):
          dataOut({'name': "customProperty", 'value': cybcon_was.showAttribute(CusProp, 'value'), 'description': cybcon_was.showAttribute(CusProp, 'name'), 'tagname': "property"});
        if CusProp == "":
          dataOut({'value': "No custom properties set."});
        dataOut({'tagname': "customproperties", 'tagtype': "2"});
        dataOut({'tagname': "interceptor", 'tagtype': "2"});
      else:
        dataOut({'value': "No interceptors found in this trust association."});
    dataOut({'tagname': "interceptors", 'tagtype': "2"});
  else:
    dataOut({'description': "WARNING", 'value': "no trust association found in LTPA"});
  dataOut({'tagname': "trustassociation", 'tagtype': "2"});
  dataOut({'tagname': "ltpa", 'tagtype': "2"});
  dataOut({'tagname': "authenticationmechanisms", 'tagtype': "2"});

  dataOut({'description': "JAAS Configuration", 'tagname': "jaasconfiguration", 'tagtype': "1"});
  dataOut({'description': "J2C Authentication data", 'tagname': "j2cauthenticationdatas", 'tagtype': "1"});
  for JAASAuthData in AdminConfig.list('JAASAuthData', securityID).split(lineSeparator):
    if JAASAuthData != "":
      dataOut({'tagname': "j2cauthenticationdata", 'tagtype': "1"});
      dataOut({'name': "alias", 'value': cybcon_was.showAttribute(JAASAuthData, 'alias'), 'description': "Alias", 'tagname': "alias"});
      dataOut({'name': "userId", 'value': cybcon_was.showAttribute(JAASAuthData, 'userId'), 'description': "User ID", 'tagname': "userid"});
      dataOut({'name': "password", 'value': cybcon_was.showAttribute(JAASAuthData, 'password'), 'description': "Password", 'tagname': "password"});
      dataOut({'name': "description", 'value': cybcon_was.showAttribute(JAASAuthData, 'description'), 'description': "Description", 'tagname': "description"});
      dataOut({'tagname': "j2cauthenticationdata", 'tagtype': "2"});
    else:
      dataOut({'value': "No J2C authentication data exists in JAAS configuration."});
  dataOut({'tagname': "j2cauthenticationdatas", 'tagtype': "2"});
  dataOut({'tagname': "jaasconfiguration", 'tagtype': "2"});
  dataOut({'tagname': "authentication", 'tagtype': "2"});

  dataOut({'description': "SSL certificate and key management", 'tagname': "sslcertificateandkeymanagement", 'tagtype': "1"});

  dataOut({'description': "Key stores and certificates", 'tagname': "keystoresandcerts", 'tagtype': "1"});
  # define possible certificate attributes to scan for and their description
  certAttributeList=['alias', 'version', 'size', 'serialNumber', 'issuedTo', 'issuedBy', 'fingerPrint', 'signatureAlgorithm', 'validity' ];

  # check if server supports AdminTask.listKeyStores()
  try:
    # check for all available KeyStores on all management scopes
    myScopedKeyStores = [];
    myOverallKeyStores = [];
    for certScope in AdminTask.listManagementScopes().split(lineSeparator):
      myTempKeyHash = {};
      myTempKeyHash['scope'] = certScope.replace("scopeName:", "").strip();
      myTempKeyHash['keystores'] = [];
      for keyStoreID in AdminTask.listKeyStores('[-scopeName "' + myTempKeyHash['scope'] + '"]').split(lineSeparator):
        if keyStoreID != "" and cybcon_was.find_valueInArray(keyStoreID, myOverallKeyStores) != 'true':
          myOverallKeyStores.append(keyStoreID);
          myTempKeyHash['keystores'].append(keyStoreID);
      if len(myTempKeyHash['keystores']) >= 1: myScopedKeyStores.append(myTempKeyHash);

    # housekeeping
    del myOverallKeyStores;
    del myTempKeyHash;

    for myKeyStoreHash in myScopedKeyStores:
      for keyStoreID in myKeyStoreHash['keystores']:
        dataOut({'tagname': "keystore", 'tagtype': "1"});
        keyStoreName = cybcon_was.showAttribute(keyStoreID, 'name');
        dataOut({'name': "name", 'value': keyStoreName, 'description': "Name", 'tagname': "name"});
        dataOut({'name': "scopeName", 'value': myKeyStoreHash['scope'], 'description': "scopeName", 'tagname': "scopeName"});
        dataOut({'name': "location", 'value': cybcon_was.showAttribute(keyStoreID, 'location'), 'description': "Path", 'tagname': "location"});
        dataOut({'name': "password", 'value': cybcon_was.showAttribute(keyStoreID, 'password'), 'description': "Password", 'tagname': "password"});
        dataOut({'name': "type", 'value': cybcon_was.showAttribute(keyStoreID, 'type'), 'description': "Type", 'tagname': "type"});
        dataOut({'name': "readOnly", 'value': cybcon_was.showAttribute(keyStoreID, 'readOnly'), 'description': "Read only", 'tagname': "readOnly"});
        dataOut({'name': "initializeAtStartup", 'value': cybcon_was.showAttribute(keyStoreID, 'initializeAtStartup'), 'description': "Initialize at startup", 'tagname': "initializeAtStartup"});
        dataOut({'name': "useForAcceleration", 'value': cybcon_was.showAttribute(keyStoreID, 'useForAcceleration'), 'description': "Enable cryptographic operations on hardware device", 'tagname': "useForAcceleration"});

        # get the signer certificates from keystore
        get_signerCertificates(keyStoreName, myKeyStoreHash, certAttributeList);

        # get the personal certificates from keystore
        get_personalCertificates(keyStoreName, myKeyStoreHash, certAttributeList);

        dataOut({'tagname': "keystore", 'tagtype': "2"});
  except AttributeError:
    dataOut({'description': "WARNING", 'value': "The Server not supports AdminTask.listKeyStores().", 'tagname': "WARNING"});
    pass;
  except:
    dataOut({'description': "ERROR", 'value': "Exception raised while executing AdminTask.listKeyStores().", 'tagname': "ERROR"});
    pass;

  dataOut({'tagname': "keystoresandcerts", 'tagtype': "2"});

  dataOut({'description': "Key set Groups", 'tagname': "keysetgroups", 'tagtype': "1"});
  for keySetGroupID in cybcon_was.splitArray(cybcon_was.showAttribute(securityID, 'keySetGroups')):
    dataOut({'tagname': "keysetgroup", 'tagtype': "1"});
    dataOut({'name': "name", 'value': cybcon_was.showAttribute(keySetGroupID, 'name'), 'description': "Name", 'tagname': "name"});
    dataOut({'description': "Key generation", 'tagname': "keygeneration", 'tagtype': "1"});
    dataOut({'name': "autoGenerate", 'value': cybcon_was.showAttribute(keySetGroupID, 'autoGenerate'), 'description': "Automatically generate keys", 'tagname': "autogenerate"});
    dataOut({'tagname': "keygeneration", 'tagtype': "2"});
    dataOut({'tagname': "keysetgroup", 'tagtype': "2"});
  dataOut({'tagname': "keysetgroups", 'tagtype': "2"});
  dataOut({'tagname': "sslcertificateandkeymanagement", 'tagtype': "2"});
  dataOut({'tagname': "security", 'tagtype': "2"});


#----------------------------------------------------------------------------
# get_signerCertificates
#   description: output the signer certificates from a given keystore
#   input: string keyStoreName, dictionary KeyStore, array certAttributeList
#   output: informations on stdout
#   return: -
#----------------------------------------------------------------------------
def get_signerCertificates(keyStoreName, myKeyStoreHash, certAttributeList):

  dataOut({'description': "Signer certificates", 'tagname': "signercertificates", 'tagtype': "1"});
  # skip errors while reading keystore (e.g. keystore file not exist)
  try:
    signerCertificates = AdminTask.listSignerCertificates(['-keyStoreScope "' + myKeyStoreHash['scope'] + '" -keyStoreName "' + keyStoreName + '"']);
    for signerCert in signerCertificates.split(lineSeparator):
      if signerCert != "":
        signerCert = signerCert.replace("[[", "").replace("] ]", "");
        # generate empty certificate dictionary
        certDict = {};
        for certAttribute in certAttributeList:
          certDict[certAttribute] = "";
        # loop over attribute lines
        for signerCertAttrib in signerCert.split('] ['):
          # loop over possible certificate attributes and scan line for the attributes
          for certAttribute in certAttributeList:
            certAtLen=len(certAttribute);
            if signerCertAttrib[:certAtLen].find(certAttribute) != -1:
              certDict[certAttribute] = signerCertAttrib[certAtLen:].replace("[", "").replace("]", "").strip();
              continue;
        #output certificate informations:
        if certDict['alias'] != "":
          dataOut({'tagname': "certificate", 'tagtype': "1"});
          dataOut({'name': 'alias', 'value': certDict['alias'], 'description': 'Alias', 'tagname': 'alias'});
          dataOut({'name': 'version', 'value': certDict['version'], 'description': 'Version', 'tagname': 'version'});
          dataOut({'name': 'size', 'value': certDict['size'], 'description': 'Key size', 'unit': 'bits', 'tagname': 'size'});
          dataOut({'name': 'serialNumber', 'value': certDict['serialNumber'], 'description': 'Serial number', 'tagname': 'serialNumber'});
          dataOut({'name': 'validity', 'value': certDict['validity'], 'description': 'Validity period', 'tagname': 'validity'});
          dataOut({'name': 'issuedTo', 'value': certDict['issuedTo'], 'description': 'Issued to', 'tagname': 'issuedTo'});
          dataOut({'name': 'issuedBy', 'value': certDict['issuedBy'], 'description': 'Issued by', 'tagname': 'issuedBy'});
          dataOut({'name': 'fingerPrint', 'value': certDict['fingerPrint'], 'description': 'Fingerprint (SHA digest)', 'tagname': 'fingerPrint'});
          dataOut({'name': 'signatureAlgorithm', 'value': certDict['signatureAlgorithm'], 'description': 'Signature algorithm', 'tagname': 'signatureAlgorithm'});
          dataOut({'tagname': "certificate", 'tagtype': "2"});
        else:
          dataOut({'value': "No signer certificate exist in keystore."});
      else:
        dataOut({'value': "No signer certificate exist in keystore."});
  except:
    dataOut({'description': "ERROR", 'value': "Exception raised while executing AdminTask.listSignerCertificates() to list certificates", 'tagname': "ERROR"});
    pass;
  dataOut({'tagname': "signercertificates", 'tagtype': "2"});

#----------------------------------------------------------------------------
# get_personalCertificates
#   description: output the personal certificates from a given keystore
#   input: string keyStoreName, dictionary KeyStore, array certAttributeList
#   output: informations on stdout
#   return: -
#----------------------------------------------------------------------------
def get_personalCertificates(keyStoreName, myKeyStoreHash, certAttributeList):
  dataOut({'description': "Personal certificates", 'tagname': "personalcertificates", 'tagtype': "1"});
  # skip errors while reading keystore (e.g. keystore file not exist)
  try:
    personalCertificates = AdminTask.listPersonalCertificates(['-keyStoreScope "' + myKeyStoreHash['scope'] + '" -keyStoreName "' + keyStoreName + '"']);
    for personalCert in personalCertificates.split(lineSeparator):
      if personalCert != "":
        personalCert = personalCert.replace("[[", "").replace("] ]", "");
        # generate empty certificate dictionary
        certDict = {};
        for certAttribute in certAttributeList:
          certDict[certAttribute] = "";
        # loop over attribute lines
        for personalCertAttrib in personalCert.split('] ['):
          # loop over possible certificate attributes and scan line for the attributes
          for certAttribute in certAttributeList:
            certAtLen=len(certAttribute);
            if personalCertAttrib[:certAtLen].find(certAttribute) != -1:
              certDict[certAttribute] = personalCertAttrib[certAtLen:].replace("[", "").replace("]", "").strip();
              continue;
        #output certificat informations:
        if certDict['alias'] != "":
          dataOut({'tagname': "certificate", 'tagtype': "1"});
          dataOut({'name': 'alias', 'value': certDict['alias'], 'description': 'Alias', 'tagname': 'alias'});
          dataOut({'name': 'version', 'value': certDict['version'], 'description': 'Version', 'tagname': 'version'});
          dataOut({'name': 'size', 'value': certDict['size'], 'description': 'Key size', 'unit': 'bits', 'tagname': 'size'});
          dataOut({'name': 'serialNumber', 'value': certDict['serialNumber'], 'description': 'Serial number', 'tagname': 'serialNumber'});
          dataOut({'name': 'validity', 'value': certDict['validity'], 'description': 'Validity period', 'tagname': 'validity'});
          dataOut({'name': 'issuedTo', 'value': certDict['issuedTo'], 'description': 'Issued to', 'tagname': 'issuedTo'});
          dataOut({'name': 'issuedBy', 'value': certDict['issuedBy'], 'description': 'Issued by', 'tagname': 'issuedBy'});
          dataOut({'name': 'fingerPrint', 'value': certDict['fingerPrint'], 'description': 'Fingerprint (SHA digest)', 'tagname': 'fingerPrint'});
          dataOut({'name': 'signatureAlgorithm', 'value': certDict['signatureAlgorithm'], 'description': 'Signature algorithm', 'tagname': 'signatureAlgorithm'});
          dataOut({'tagname': "certificate", 'tagtype': "2"});
        else:
          dataOut({'value': "No personal certificate exist in keystore."});
      else:
        dataOut({'value': "No personal certificate exist in keystore."});
  except:
    dataOut({'description': "ERROR", 'value': "Exception raised while executing AdminTask.listPersonalCertificates() to list certificates", 'tagname': "ERROR"});
    pass;
  dataOut({'tagname': "personalcertificates", 'tagtype': "2"});

#----------------------------------------------------------------------------
# get_virtualHostProperties
#   description: searching all virtual hosts defined in the cell and the
#     hosta aliases and output them
#   input: cellID
#   output: informations on stdout
#   return: -
#----------------------------------------------------------------------------
def get_virtualHostProperties(cellID):
  dataOut({'description': "Virtual Hosts", 'tagname': "virtualhosts", 'tagtype': "1"});
  for virtualHostID in AdminConfig.list('VirtualHost', cellID).split(lineSeparator):
    if virtualHostID != "":
      dataOut({'tagname': "virtualhost", 'tagtype': "1"});
      dataOut({'name': "name", 'value': cybcon_was.showAttribute(virtualHostID, 'name'), 'description': "Name", 'tagname': "name"});
      dataOut({'description': "Host Aliases", 'tagname': "hostaliases", 'tagtype': "1"});
      for hostAliasID in cybcon_was.showAttribute(virtualHostID, 'aliases').split():
        hostAliasID = hostAliasID.replace("[", "").replace("]", "");
        if hostAliasID != "":
          dataOut({'tagname': "hostalias", 'tagtype': "1"});
          dataOut({'name': "hostname", 'value': cybcon_was.showAttribute(hostAliasID, 'hostname'), 'description': "Host Name", 'tagname': "hostname"});
          dataOut({'name': "port", 'value': cybcon_was.showAttribute(hostAliasID, 'port'), 'description': "Port", 'tagname': "port"});
          dataOut({'tagname': "hostalias", 'tagtype': "2"});
        else:
          dataOut({'value': "No host alias defined for this virtual host."});
      dataOut({'tagname': "hostaliases", 'tagtype': "2"});
      dataOut({'tagname': "virtualhost", 'tagtype': "2"});
    else:
      dataOut({'value': "No virtual hosts defined in cell."});
      continue;
  dataOut({'tagname': "virtualhosts", 'tagtype': "2"});


#----------------------------------------------------------------------------
# get_variables
#   description: search the WebSphere variables by it's given objectID
#   input: objectID (can be cellID, clusterID, nodeID or serverID)
#   output: informations on stdout
#   return: -
#----------------------------------------------------------------------------
def get_variables(objectID):
  dataOut({'description': "WebSphere Variables", 'tagname': "webspherevariables", 'tagtype': "1"});
# get name and objectType of the objectID
  objectName = cybcon_was.showAttribute(objectID, 'name');
  objectType = cybcon_was.get_ObjectTypeByID(objectID);
  if objectType == "Server":
    nodeName = cybcon_was.get_nodeNameByServerID(objectID);
    if nodeName != "": objectType = 'Node:' + nodeName + '/' + objectType;
# get IDs, searching by scope, and type
  for variableMap in AdminConfig.getid('/' + objectType + ':' + objectName + '/VariableMap:/').split(lineSeparator):
    if variableMap != "":
      variableEntry = "";
      for variableEntry in cybcon_was.splitArray(cybcon_was.showAttribute(variableMap, 'entries')):
        dataOut({'name': "entry", 'value': cybcon_was.showAttribute(variableEntry, 'value'), 'description': cybcon_was.showAttribute(variableEntry, 'symbolicName'), 'tagname': "property"});
      if variableEntry == "":
        dataOut({'value': "No variables set on this scope."});
    else:
      dataOut({'value': "No variables set on this scope."});
      continue;
  dataOut({'tagname': "webspherevariables", 'tagtype': "2"});

#----------------------------------------------------------------------------
# get_sharedLibraryProperties
#   description: output the relevant informations of installed shared
#     libraries on objectID level
#   input: objectID (can be cellID, clusterID, nodeID or serverID)
#   output: informations on stdout
#   return: -
#----------------------------------------------------------------------------
def get_sharedLibraryProperties(objectID):
  dataOut({'description': "Shared Libraries", 'tagname': "sharedlibraries", 'tagtype': "1"});
# get name and objectType of the objectID
  objectName = cybcon_was.showAttribute(objectID, 'name');
  objectType = cybcon_was.get_ObjectTypeByID(objectID);
  if objectType == "Server":
    nodeName = cybcon_was.get_nodeNameByServerID(objectID);
    if nodeName != "": objectType = 'Node:' + nodeName + '/' + objectType;
# get IDs, searching by scope, and type
  for SharedLib in AdminConfig.getid('/' + objectType + ':' + objectName + '/Library:/').split(lineSeparator):
    if SharedLib != "":
      dataOut({'tagname': "sharedlibrary", 'tagtype': "1"});
      dataOut({'name': "name", 'value': cybcon_was.showAttribute(SharedLib, 'name'), 'description': "Name", 'tagname': "name"});
      dataOut({'name': "description", 'value': cybcon_was.showAttribute(SharedLib, 'description'), 'description': "Description", 'tagname': "description"});
      dataOut({'name': "classPath", 'value': cybcon_was.showAttribute(SharedLib, 'classPath'), 'description': "Classpath", 'tagname': "classPath"});
      dataOut({'tagname': "sharedlibrary", 'tagtype': "2"});
    else:
      dataOut({'value': "No shared libraries defined on this scope."});
  dataOut({'tagname': "sharedlibraries", 'tagtype': "2"});

#----------------------------------------------------------------------------
# get_nameSpaceBindingProperties
#   description: output the usefull naming informations on given objectID
#     level
#   input: objectID (can be cellID, nodeID or serverID)
#   output: informations on stdout
#   return: -
#----------------------------------------------------------------------------
def get_nameSpaceBindingProperties(objectID):
  dataOut({'description': "Name Space Bindings", 'tagname': "namespacebindings", 'tagtype': "1"});

  # get name and objectType of the objectID
  objectName = cybcon_was.showAttribute(objectID, 'name');
  objectType = cybcon_was.get_ObjectTypeByID(objectID);
  if objectType == "Server":
    nodeName = cybcon_was.get_nodeNameByServerID(objectID);
    if nodeName != "": objectType = 'Node:' + nodeName + '/' + objectType;

  # get string NSBs
  #for NSB in AdminConfig.list('StringNameSpaceBinding', objectID).split(lineSeparator):
  for NSB in AdminConfig.getid('/' + objectType + ':' + objectName + '/StringNameSpaceBinding:/').split(lineSeparator):
    if NSB != "":
      dataOut({'tagname': "namespacebinding", 'tagprops': [ "bindingtype='string'" ], 'tagtype': "1"});
      dataOut({'name': 'bindingtype', 'value': 'string', 'description': 'Binding type', 'tagname': 'bindingtype'});
      n = cybcon_was.showAttribute(NSB, 'name');
      dataOut({'name': "name", 'value': n, 'description': "Binding Identifier", 'tagname': "name"});
      nins = cybcon_was.showAttribute(NSB, 'nameInNameSpace');
      dataOut({'name': "nameInNameSpace", 'value': nins, 'description': "Name in Name Space", 'tagname': "nameinnamespace"});
      pwcheck = n + nins;
      if pwcheck.lower().find("password") != -1 and CONFIG['general']['LogPasswords'] != "true":
        v = "***skipped by policy***";
      else:
        v = cybcon_was.showAttribute(NSB, 'stringToBind');
      dataOut({'name': "stringToBind", 'value': v, 'description': "String Value", 'tagname': "stringtobind"});
      dataOut({'tagname': "namespacebinding", 'tagtype': "2"});

  # get EJB NSBs
  for NSB in AdminConfig.getid('/' + objectType + ':' + objectName + '/EjbNameSpaceBinding:/').split(lineSeparator):
    if NSB != "":
      dataOut({'tagname': "namespacebinding", 'tagprops': [ "bindingtype='Ejb'" ], 'tagtype': "1"});
      dataOut({'name': 'bindingtype', 'value': 'Ejb', 'description': 'Binding type', 'tagname': 'bindingtype'});
      dataOut({'name': "name", 'value': cybcon_was.showAttribute(NSB, 'name'), 'description': "Binding Identifier", 'tagname': "name"});
      dataOut({'name': "nameInNameSpace", 'value': cybcon_was.showAttribute(NSB, 'nameInNameSpace'), 'description': "Name in Name Space", 'tagname': "nameinnamespace"});
      dataOut({'name': 'bindingLocation', 'value': cybcon_was.showAttribute(NSB, 'bindingLocation'), 'description': 'Enterprise Bean Location', 'tagname': 'bindingLocation'});
      dataOut({'name': 'applicationServerName', 'value': cybcon_was.showAttribute(NSB, 'applicationServerName'), 'description': 'Server', 'tagname': 'applicationServerName'});
      dataOut({'name': 'ejbJndiName', 'value': cybcon_was.showAttribute(NSB, 'ejbJndiName'), 'description': 'JNDI name', 'tagname': 'ejbJndiName'});
      dataOut({'tagname': "namespacebinding", 'tagtype': "2"});

  # get CORBA NSBs
  for NSB in AdminConfig.getid('/' + objectType + ':' + objectName + '/CORBAObjectNameSpaceBinding:/').split(lineSeparator):
    if NSB != "":
      dataOut({'tagname': "namespacebinding", 'tagprops': [ "bindingtype='CORBA'" ], 'tagtype': "1"});
      dataOut({'name': 'bindingtype', 'value': 'CORBA', 'description': 'Binding type', 'tagname': 'bindingtype'});
      dataOut({'name': "name", 'value': cybcon_was.showAttribute(NSB, 'name'), 'description': "Binding Identifier", 'tagname': "name"});
      dataOut({'name': "nameInNameSpace", 'value': cybcon_was.showAttribute(NSB, 'nameInNameSpace'), 'description': " Name in name space relative to lookup name prefix", 'tagname': "nameinnamespace"});
      dataOut({'name': 'corbanameUrl', 'value': cybcon_was.showAttribute(NSB, 'corbanameUrl'), 'description': 'Corbaname URL', 'tagname': 'corbanameUrl'});
      dataOut({'name': 'federatedContext', 'value': cybcon_was.showAttribute(NSB, 'federatedContext'), 'description': 'Federated context', 'tagname': 'federatedContext'});
      dataOut({'tagname': "namespacebinding", 'tagtype': "2"});

  # get Indirect lookup NSBs
  for NSB in AdminConfig.getid('/' + objectType + ':' + objectName + '/IndirectLookupNameSpaceBinding:/').split(lineSeparator):
    if NSB != "":
      dataOut({'tagname': "namespacebinding", 'tagprops': [ "bindingtype='Indirect'" ], 'tagtype': "1"});
      dataOut({'name': 'bindingtype', 'value': 'Indirect', 'description': 'Binding type', 'tagname': 'bindingtype'});
      dataOut({'name': "name", 'value': cybcon_was.showAttribute(NSB, 'name'), 'description': "Binding Identifier", 'tagname': "name"});
      dataOut({'name': "nameInNameSpace", 'value': cybcon_was.showAttribute(NSB, 'nameInNameSpace'), 'description': " Name in name space relative to lookup name prefix", 'tagname': "nameinnamespace"});
      dataOut({'name': 'providerURL', 'value': cybcon_was.showAttribute(NSB, 'providerURL'), 'description': 'Provider URL', 'tagname': 'providerURL'});
      dataOut({'name': 'jndiName', 'value': cybcon_was.showAttribute(NSB, 'jndiName'), 'description': 'JNDI name', 'tagname': 'jndiName'});
      dataOut({'tagname': "namespacebinding", 'tagtype': "2"});

  dataOut({'tagname': "namespacebindings", 'tagtype': "2"});

#----------------------------------------------------------------------------
# get_appServerProperties
#   description: get all helpfull and often changed configurations from the
#     application servermember
#   input: serverID, serverName
#   output: informations on stdout
#   return: -
#----------------------------------------------------------------------------
def get_appServerProperties(serverID, serverName):
  dataOut({'description': "Standard application server settings", 'tagname': "standardapplicationserversettings", 'tagtype': "1"});
  dataOut({'name': "applicationClassLoaderPolicy", 'value': cybcon_was.showAttribute(AdminConfig.list('ApplicationServer', serverID), 'applicationClassLoaderPolicy'), 'description': "Classloader policy", 'tagname': "applicationClassLoaderPolicy"});
  dataOut({'name': "applicationClassLoadingMode", 'value': cybcon_was.showAttribute(AdminConfig.list('ApplicationServer', serverID), 'applicationClassLoadingMode'), 'description': "Class loading mode", 'tagname': "applicationClassLoadingMode"});
  dataOut({'tagname': "standardapplicationserversettings", 'tagtype': "2"});

  dataOut({'description': "Container Settings", 'tagname': "containersettings", 'tagtype': "1"});
  dataOut({'description': "Web Container Settings", 'tagname': "webcontainersettings", 'tagtype': "1"});
  dataOut({'description': "Web Container", 'tagname': "webcontainer", 'tagtype': "1"});
  for WCID in AdminConfig.list('WebContainer', serverID).split(lineSeparator):
    if WCID != "":
      dataOut({'name': "defaultVirtualHostName", 'value': cybcon_was.showAttribute(WCID, 'defaultVirtualHostName'), 'description': "Default virtual host", 'tagname': "defaultVirtualHostName"});
      dataOut({'name': "enableServletCaching", 'value': cybcon_was.showAttribute(WCID, 'enableServletCaching'), 'description': "Enable servlet caching", 'tagname': "enableServletCaching"});
      dataOut({'description': "Custom properties", 'tagname': "customproperties", 'tagtype': "1"});
      CusProp="";
      for CusProp in cybcon_was.splitArray(cybcon_was.showAttribute(WCID, 'properties')):
        dataOut({'name': "customProperty", 'value': cybcon_was.showAttribute(CusProp, 'value'), 'description': cybcon_was.showAttribute(CusProp, 'name'), 'tagname': "property"});
      if CusProp == "":
        dataOut({'value': "No custom properties set."});
      dataOut({'tagname': "customproperties", 'tagtype': "2"});
      dataOut({'description': "Session management", 'tagname': "sessionmanagement", 'tagtype': "1"});
      for SMID in cybcon_was.showAttribute(WCID, 'services').replace("[", "").replace("]", "").split(" "):
        if SMID != "":
          dataOut({'tagname': "sessionservice", 'tagtype': "1"});
          dataOut({'description': "Session tracking mechanism", 'tagname': "sessiontrackingmechanism", 'tagtype': "1"});
          dataOut({'name': "enableSSLTracking", 'value': cybcon_was.showAttribute(SMID, 'enableSSLTracking'), 'description': "Enable SSL ID tracking", 'tagname': "enableSSLTracking"});
          dataOut({'name': "enableCookies", 'value': cybcon_was.showAttribute(SMID, 'enableCookies'), 'description': "Enable cookies", 'tagname': "enableCookies"});
          dataOut({'tagname': "cookies", 'tagtype': "1"});
          dataOut({'name': "name", 'value': cybcon_was.showAttribute(cybcon_was.showAttribute(SMID, 'defaultCookieSettings'), 'name'), 'description': "Cookie name", 'tagname': "name"});
          dataOut({'name': "secure", 'value': cybcon_was.showAttribute(cybcon_was.showAttribute(SMID, 'defaultCookieSettings'), 'secure'), 'description': "Restrict cookies to HTTPS sessions", 'tagname': "secure"});
          dataOut({'name': "domain", 'value': cybcon_was.showAttribute(cybcon_was.showAttribute(SMID, 'defaultCookieSettings'), 'domain'), 'description': "Cookie domain", 'tagname': "domain"});
          dataOut({'name': "path", 'value': cybcon_was.showAttribute(cybcon_was.showAttribute(SMID, 'defaultCookieSettings'), 'path'), 'description': "Cookie path", 'tagname': "path"});
          dataOut({'description': "Cookie maximum age", 'tagname': "cookiemaximumage", 'tagtype': "1"});
          cma = cybcon_was.showAttribute(cybcon_was.showAttribute(SMID, 'defaultCookieSettings'), 'maximumAge');
          if cma == -1:
            dataOut({'value': "selected", 'description': "Current browser session", 'tagname': "currentbrowsersession"});
            dataOut({'name': "maximumAge", 'value': cma, 'unit': "seconds", 'description': "Set maximum age", 'tagname': "maximumAge"});
          else:
            dataOut({'value': "not selected", 'description': "Current browser session", 'tagname': "currentbrowsersession"});
            dataOut({'name': "maximumAge", 'value': cma, 'unit': "seconds", 'description': "Set maximum age", 'tagname': "maximumAge"});
          dataOut({'tagname': "cookiemaximumage", 'tagtype': "2"});
          dataOut({'tagname': "cookies", 'tagtype': "2"});
          dataOut({'name': "enableUrlRewriting", 'value': cybcon_was.showAttribute(SMID, 'enableUrlRewriting'), 'description': "Enable URL rewriting", 'tagname': "enableUrlRewriting"});
          dataOut({'tagname': "urlrewriting", 'tagtype': "1"});
          dataOut({'name': "enableProtocolSwitchRewriting", 'value': cybcon_was.showAttribute(SMID, 'enableProtocolSwitchRewriting'), 'description': "Enable protocol switch rewriting", 'tagname': "enableProtocolSwitchRewriting"});
          dataOut({'tagname': "urlrewriting", 'tagtype': "2"});
          dataOut({'tagname': "sessiontrackingmechanism", 'tagtype': "2"});

          dataOut({'name': "maxInMemorySessionCount", 'value': cybcon_was.showAttribute(cybcon_was.showAttribute(SMID, 'tuningParams'), 'maxInMemorySessionCount'), 'description': "Maximum in-memory session count", 'tagname': "maxInMemorySessionCount"});
          dataOut({'name': "allowOverflow", 'value': cybcon_was.showAttribute(cybcon_was.showAttribute(SMID, 'tuningParams'), 'allowOverflow'), 'description': "Allow overflow", 'tagname': "allowOverflow"});
          dataOut({'description': "Session timeout", 'tagname': "sessiontimeout", 'tagtype': "1"});
          if cybcon_was.showAttribute(cybcon_was.showAttribute(SMID, 'tuningParams'), 'invalidationTimeout') == -1:
            dataOut({'value': "selected", 'description': "No timeout", 'tagname': "timeoutselection"});
          else:
            dataOut({'value': "selected", 'description': "Set timeout", 'tagname': "timeoutselection"});
            dataOut({'name': "invalidationTimeout", 'value': cybcon_was.showAttribute(cybcon_was.showAttribute(SMID, 'tuningParams'), 'invalidationTimeout'), 'unit': "minutes", 'description': "Timeout", 'tagname': "invalidationTimeout"});
          dataOut({'tagname': "sessiontimeout", 'tagtype': "2"});
          dataOut({'name': "enableSecurityIntegration", 'value': cybcon_was.showAttribute(SMID, 'enableSecurityIntegration'), 'description': "Security integration", 'tagname': "enableSecurityIntegration"});
          dataOut({'description': "Serialize session access", 'tagname': "serializesessionaccess", 'tagtype': "1"});
          dataOut({'name': "allowSerializedSessionAccess", 'value': cybcon_was.showAttribute(SMID, 'allowSerializedSessionAccess'), 'description': "Allow serial access", 'tagname': "allowSerializedSessionAccess"});
          dataOut({'tagname': "serializedsessionparameters", 'tagtype': "1"});
          dataOut({'name': "maxWaitTime", 'value': cybcon_was.showAttribute(SMID, 'maxWaitTime'), 'unit': "seconds", 'description': "Maximum wait time", 'tagname': "maxWaitTime"});
          dataOut({'name': "accessSessionOnTimeout", 'value': cybcon_was.showAttribute(SMID, 'accessSessionOnTimeout'), 'description': "Allow access on timeout", 'tagname': "accessSessionOnTimeout"});
          dataOut({'tagname': "serializedsessionparameters", 'tagtype': "2"});
          dataOut({'tagname': "serializesessionaccess", 'tagtype': "2"});
          dataOut({'tagname': "sessionservice", 'tagtype': "2"});
        else:
          dataOut({'value': "No Session management properties exists."});
      dataOut({'tagname': "sessionmanagement", 'tagtype': "2"});
  dataOut({'tagname': "webcontainer", 'tagtype': "2"});

  dataOut({'description': "Web Container transport chains", 'tagname': "webcontainertransportchains", 'tagtype': "1"});
  for tranChServiceID in AdminConfig.getid('/Server:' + serverName + '/TransportChannelService:/').split(lineSeparator):
    if tranChServiceID != "":
      dataOut({'tagname': "TransportChannelService", 'tagtype': "1"});
      dataOut({'tagname': "chains", 'tagtype': "1"});
      for chainID in cybcon_was.showAttribute(tranChServiceID, 'chains').replace("[", "").replace("]", "").split(" "):
        if chainID.startswith("WC"):
          dataOut({'tagname': "chain", 'tagtype': "1"});
          dataOut({'name': "name", 'value': cybcon_was.showAttribute(chainID, 'name'), 'description': "Name", 'tagname': "name"});
          dataOut({'name': "enable", 'value': cybcon_was.showAttribute(chainID, 'enable'), 'description': "Enabled", 'tagname': "enable"});
          if cybcon_was.showAttribute(chainID, 'enable') == "true":
            dataOut({'description': "Transport Channels", 'tagname': "transportchannels", 'tagtype': "1"});
            for tranChanID in cybcon_was.showAttribute(chainID, 'transportChannels').replace("[", "").replace("]", "").split(" "):
              if tranChanID.startswith("TCP"):
                n = cybcon_was.showAttribute(tranChanID, 'name');
                dataOut({'description': "TCP Inbound Channel (" + n + ")", 'tagname': "transportchannel", 'tagtype': "1"});
                dataOut({'name': "name", 'value': n, 'description': "Name", 'tagname': "name"});
                dataOut({'name': "endPointName", 'value': cybcon_was.showAttribute(tranChanID, 'endPointName'), 'description': "Port", 'tagname': "endPointName"});
                threadPoolID = cybcon_was.showAttribute(tranChanID, 'threadPool');
                dataOut({'description': "Thread Pool", 'tagname': "threadpool", 'tagtype': "1"});
                if threadPoolID != "":
                  dataOut({'name': "name", 'value': cybcon_was.showAttribute(threadPoolID, 'name'), 'description': "Name", 'tagname': "name"});
                  dataOut({'name': "minimumSize", 'value': cybcon_was.showAttribute(threadPoolID, 'minimumSize'), 'unit': "threads", 'description': "Minimum Size", 'tagname': "minimumSize"});
                  dataOut({'name': "maximumSize", 'value': cybcon_was.showAttribute(threadPoolID, 'maximumSize'), 'unit': "threads", 'description': "Maximum Size", 'tagname': "maximumSize"});
                  dataOut({'name': "inactivityTimeout", 'value': cybcon_was.showAttribute(threadPoolID, 'inactivityTimeout'), 'unit': "milliseconds", 'description': "Thread inactivity timeout", 'tagname': "inactivityTimeout"});
                  dataOut({'name': "isGrowable", 'value': cybcon_was.showAttribute(threadPoolID, 'isGrowable'), 'description': "Allow thread allocation beyond maximum thread size", 'tagname': "isGrowable"});
                dataOut({'tagname': "threadpool", 'tagtype': "2"});
                dataOut({'name': "maxOpenConnections", 'value': cybcon_was.showAttribute(tranChanID, 'maxOpenConnections'), 'description': "Maximum open connections", 'tagname': "maxOpenConnections"});
                dataOut({'name': "inactivityTimeout", 'value': cybcon_was.showAttribute(tranChanID, 'inactivityTimeout'), 'unit': "seconds", 'description': "Inactivity timeout", 'tagname': "inactivityTimeout"});
                dataOut({'name': "addressExcludeList", 'value': cybcon_was.showAttribute(tranChanID, 'addressExcludeList'), 'description': "Address exclude list", 'tagname': "addressExcludeList"});
                dataOut({'name': "addressIncludeList", 'value': cybcon_was.showAttribute(tranChanID, 'addressIncludeList'), 'description': "Address include list", 'tagname': "addressIncludeList"});
                dataOut({'name': "hostNameExcludeList", 'value': cybcon_was.showAttribute(tranChanID, 'hostNameExcludeList'), 'description': "Hostname exclude list", 'tagname': "hostNameExcludeList"});
                dataOut({'name': "hostNameIncludeList", 'value': cybcon_was.showAttribute(tranChanID, 'hostNameIncludeList'), 'description': "Hostname include list", 'tagname': "hostNameIncludeList"});
                dataOut({'description': "Custom properties", 'tagname': "customproperties", 'tagtype': "1"});
                CusProp="";
                for CusProp in cybcon_was.splitArray(cybcon_was.showAttribute(tranChanID, 'properties')):
                  dataOut({'name': "customProperty", 'value': cybcon_was.showAttribute(CusProp, 'value'), 'description': cybcon_was.showAttribute(CusProp, 'name'), 'tagname': "property"});
                if CusProp == "":
                  dataOut({'value': "No custom properties set."});
                dataOut({'tagname': "customproperties", 'tagtype': "2"});
                dataOut({'tagname': "transportchannel", 'tagtype': "2"});

              elif tranChanID.startswith("SSL"):
                n = cybcon_was.showAttribute(tranChanID, 'name');
                dataOut({'description': "SSL Inbound Channel (" + n + ")", 'tagname': "transportchannel", 'tagtype': "1"});
                dataOut({'name': "name", 'value': n, 'description': "Name", 'tagname': "name"});
                dataOut({'name': "discriminationWeight", 'value': cybcon_was.showAttribute(tranChanID, 'discriminationWeight'), 'description': "Discrimination weight", 'tagname': "discriminationWeight"});
                dataOut({'name': "sslConfigAlias", 'value': cybcon_was.showAttribute(tranChanID, 'sslConfigAlias'), 'description': "SSL repertoire", 'tagname': "sslConfigAlias"});
                dataOut({'description': "Custom properties", 'tagname': "customproperties", 'tagtype': "1"});
                CusProp="";
                for CusProp in cybcon_was.splitArray(cybcon_was.showAttribute(tranChanID, 'properties')):
                  dataOut({'name': "customProperty", 'value': cybcon_was.showAttribute(CusProp, 'value'), 'description': cybcon_was.showAttribute(CusProp, 'name'), 'tagname': "property"});
                if CusProp == "":
                  dataOut({'value': "No custom properties set."});
                dataOut({'tagname': "customproperties", 'tagtype': "2"});
                dataOut({'tagname': "transportchannel", 'tagtype': "2"});

              elif tranChanID.startswith("HTTP"):
                n = cybcon_was.showAttribute(tranChanID, 'name');
                dataOut({'description': "HTTP Inbound Channel (" + n + ")", 'tagname': "transportchannel", 'tagtype': "1"});
                dataOut({'name': "name", 'value': n, 'description': "Name", 'tagname': "name"});
                dataOut({'name': "discriminationWeight", 'value': cybcon_was.showAttribute(tranChanID, 'discriminationWeight'), 'description': "Discrimination weight", 'tagname': "discriminationWeight"});
                dataOut({'name': "maximumPersistentRequests", 'value': cybcon_was.showAttribute(tranChanID, 'maximumPersistentRequests'), 'description': "Maximum persistent requests", 'tagname': "maximumPersistentRequests"});
                dataOut({'name': "keepAlive", 'value': cybcon_was.showAttribute(tranChanID, 'keepAlive'), 'description': "Use persistent (keep-alive) connections", 'tagname': "keepAlive"});
                dataOut({'name': "readTimeout", 'value': cybcon_was.showAttribute(tranChanID, 'readTimeout'), 'description': "Read timeout", 'tagname': "readTimeout"});
                dataOut({'name': "writeTimeout", 'value': cybcon_was.showAttribute(tranChanID, 'writeTimeout'), 'description': "Write timeout", 'tagname': "writeTimeout"});
                dataOut({'name': "persistentTimeout", 'value': cybcon_was.showAttribute(tranChanID, 'persistentTimeout'), 'description': "Persistent timeout", 'tagname': "persistentTimeout"});
                dataOut({'name': "enableLogging", 'value': cybcon_was.showAttribute(tranChanID, 'enableLogging'), 'description': "Enable access and error logging", 'tagname': "enableLogging"});
                dataOut({'description': "Custom properties", 'tagname': "customproperties", 'tagtype': "1"});
                CusProp="";
                for CusProp in cybcon_was.splitArray(cybcon_was.showAttribute(tranChanID, 'properties')):
                  dataOut({'name': "customProperty", 'value': cybcon_was.showAttribute(CusProp, 'value'), 'description': cybcon_was.showAttribute(CusProp, 'name'), 'tagname': "property"});
                if CusProp == "":
                  dataOut({'value': "No custom properties set."});
                dataOut({'tagname': "customproperties", 'tagtype': "2"});
                dataOut({'tagname': "transportchannel", 'tagtype': "2"});

              elif tranChanID.startswith("WCC"):
                n = cybcon_was.showAttribute(tranChanID, 'name');
                dataOut({'description': "Web Container Inbound Channel (" + n + ")", 'tagname': "transportchannel", 'tagtype': "1"});
                dataOut({'name': "name", 'value': n, 'description': "Name", 'tagname': "name"});
                dataOut({'name': "discriminationWeight", 'value': cybcon_was.showAttribute(tranChanID, 'discriminationWeight'), 'description': "Discrimination weight", 'tagname': "discriminationWeight"});
                dataOut({'name': "writeBufferSize", 'value': cybcon_was.showAttribute(tranChanID, 'writeBufferSize'), 'unit': "bytes", 'description': "Write buffer size", 'tagname': "writeBufferSize"});
                dataOut({'description': "Custom properties", 'tagname': "customproperties", 'tagtype': "1"});
                CusProp="";
                for CusProp in cybcon_was.splitArray(cybcon_was.showAttribute(tranChanID, 'properties')):
                  dataOut({'name': "customProperty", 'value': cybcon_was.showAttribute(CusProp, 'value'), 'description': cybcon_was.showAttribute(CusProp, 'name'), 'tagname': "property"});
                if CusProp == "":
                  dataOut({'value': "No custom properties set."});
                dataOut({'tagname': "customproperties", 'tagtype': "2"});
                dataOut({'tagname': "transportchannel", 'tagtype': "2"});
            dataOut({'tagname': "transportchannels", 'tagtype': "2"});
          dataOut({'tagname': "chain", 'tagtype': "2"});
      dataOut({'tagname': "chains", 'tagtype': "2"});
      dataOut({'tagname': "TransportChannelService", 'tagtype': "2"});
  dataOut({'tagname': "webcontainertransportchains", 'tagtype': "2"});
  dataOut({'tagname': "webcontainersettings", 'tagtype': "2"});

  dataOut({'description': "Container Services", 'tagname': "containerservices", 'tagtype': "1"});
  dataOut({'description': "Transaction Service", 'tagname': "transactionservice", 'tagtype': "1"});
  trsvID = AdminConfig.list('TransactionService', serverID);
  dataOut({'name': "totalTranLifetimeTimeout", 'value': cybcon_was.showAttribute(trsvID, 'totalTranLifetimeTimeout'), 'unit': "seconds", 'description': "Total transaction lifetime timeout", 'tagname': "totalTranLifetimeTimeout"});
  dataOut({'name': "asyncResponseTimeout", 'value': cybcon_was.showAttribute(trsvID, 'asyncResponseTimeout'), 'unit': "seconds", 'description': "Async response timeout", 'tagname': "asyncResponseTimeout"});
  dataOut({'name': "clientInactivityTimeout", 'value': cybcon_was.showAttribute(trsvID, 'clientInactivityTimeout'), 'unit': "seconds", 'description': "Client inactivity timeout", 'tagname': "clientInactivityTimeout"});
  dataOut({'name': "propogatedOrBMTTranLifetimeTimeout", 'value': cybcon_was.showAttribute(trsvID, 'propogatedOrBMTTranLifetimeTimeout'), 'unit': "seconds", 'description': "Maximum transaction timeout", 'tagname': "propogatedOrBMTTranLifetimeTimeout"});
  dataOut({'name': "heuristicRetryLimit", 'value': cybcon_was.showAttribute(trsvID, 'heuristicRetryLimit'), 'unit': "retries", 'description': "Heuristic retry limit", 'tagname': "heuristicRetryLimit"});
  dataOut({'name': "heuristicRetryWait", 'value': cybcon_was.showAttribute(trsvID, 'heuristicRetryWait'), 'unit': "seconds", 'description': "Heuristic retry wait", 'tagname': "heuristicRetryWait"});
  dataOut({'name': "enableLoggingForHeuristicReporting", 'value': cybcon_was.showAttribute(trsvID, 'enableLoggingForHeuristicReporting'), 'description': "Enable logging for heuristic reporting", 'tagname': "enableLoggingForHeuristicReporting"});
  dataOut({'name': "LPSHeuristicCompletion", 'value': cybcon_was.showAttribute(trsvID, 'LPSHeuristicCompletion'), 'description': "Heuristic completion direction", 'tagname': "LPSHeuristicCompletion"});
  dataOut({'name': "enableFileLocking", 'value': cybcon_was.showAttribute(trsvID, 'enableFileLocking'), 'description': "Enable file locking", 'tagname': "enableFileLocking"});
  dataOut({'name': "enableProtocolSecurity", 'value': cybcon_was.showAttribute(trsvID, 'enableProtocolSecurity'), 'description': "Enable protocol security", 'tagname': "enableProtocolSecurity"});
  dataOut({'tagname': "transactionservice", 'tagtype': "2"});

  dataOut({'description': "Dynamic Cache Service", 'tagname': "dynamiccacheservice", 'tagtype': "1"});
  dynaChacheID=AdminConfig.list('DynamicCache', serverID);
  dataOut({'name': "enable", 'value': cybcon_was.showAttribute(dynaChacheID, 'enable'), 'description': "Enable service at server startup", 'tagname': "enable"});
  dataOut({'name': "cacheSize", 'value': cybcon_was.showAttribute(dynaChacheID, 'cacheSize'), 'unit': "entries", 'description': "Cache size", 'tagname': "cacheSize"});
  dataOut({'name': "defaultPriority", 'value': cybcon_was.showAttribute(dynaChacheID, 'defaultPriority'), 'description': "Default priority", 'tagname': "defaultPriority"});
  dataOut({'name': "enableDiskOffload", 'value': cybcon_was.showAttribute(dynaChacheID, 'enableDiskOffload'), 'description': "Enable disk offload", 'tagname': "enableDiskOffload"});
  dataOut({'name': "enableCacheReplication", 'value': cybcon_was.showAttribute(dynaChacheID, 'enableCacheReplication'), 'description': "Enable cache replication", 'tagname': "enableCacheReplication"});
  dataOut({'name': "replicationType", 'value': cybcon_was.showAttribute(dynaChacheID, 'replicationType'), 'description': "Replication type", 'tagname': "replicationType"});
  dataOut({'name': "pushFrequency", 'value': cybcon_was.showAttribute(dynaChacheID, 'pushFrequency'), 'description': "Push frequency", 'tagname': "pushFrequency"});
  dataOut({'description': "External cache groups", 'tagname': "externalcachegroups", 'tagtype': "1"});
  extCacheGroupID="";
  for extCacheGroupID in cybcon_was.splitArray(cybcon_was.showAttribute(dynaChacheID, 'cacheGroups')):
    dataOut({'tagname': "externalcachegroup", 'tagtype': "1"});
    dataOut({'name': "name", 'value': cybcon_was.showAttribute(extCacheGroupID, 'name'), 'description': "Name", 'tagname': "name"});
    dataOut({'name': "type", 'value': cybcon_was.showAttribute(extCacheGroupID, 'type'), 'description': "Type", 'tagname': "type"});
    dataOut({'tagname': "externalcachegroup", 'tagtype': "2"});
  dataOut({'tagname': "externalcachegroups", 'tagtype': "2"});
  dataOut({'tagname': "dynamiccacheservice", 'tagtype': "2"});

  dataOut({'description': "ORB Service", 'tagname': "orbservice", 'tagtype': "1"});
  orbID = AdminConfig.list('ObjectRequestBroker', serverID);
  dataOut({'name': "requestTimeout", 'value': cybcon_was.showAttribute(orbID, 'requestTimeout'), 'unit': "seconds", 'description': "Request timeout", 'tagname': "requestTimeout"});
  dataOut({'name': "requestRetriesCount", 'value': cybcon_was.showAttribute(orbID, 'requestRetriesCount'), 'unit': "retries", 'description': "Request retries count", 'tagname': "requestRetriesCount"});
  dataOut({'name': "requestRetriesDelay", 'value': cybcon_was.showAttribute(orbID, 'requestRetriesDelay'), 'unit': "milliseconds", 'description': "Request retries delay", 'tagname': "requestRetriesDelay"});
  dataOut({'name': "connectionCacheMaximum", 'value': cybcon_was.showAttribute(orbID, 'connectionCacheMaximum'), 'unit': "connections", 'description': "Connection cache maximum", 'tagname': "connectionCacheMaximum"});
  dataOut({'name': "connectionCacheMinimum", 'value': cybcon_was.showAttribute(orbID, 'connectionCacheMinimum'), 'unit': "connections", 'description': "Connection cache minimum", 'tagname': "connectionCacheMinimum"});
  dataOut({'name': "commTraceEnabled", 'value': cybcon_was.showAttribute(orbID, 'commTraceEnabled'), 'description': "ORB tracing", 'tagname': "commTraceEnabled"});
  dataOut({'name': "locateRequestTimeout", 'value': cybcon_was.showAttribute(orbID, 'locateRequestTimeout'), 'unit': "seconds", 'description': "Locate request timeout", 'tagname': "locateRequestTimeout"});
  dataOut({'name': "forceTunnel", 'value': cybcon_was.showAttribute(orbID, 'forceTunnel'), 'description': "Force tunnel", 'tagname': "forceTunnel"});
  dataOut({'name': "noLocalCopies", 'value': cybcon_was.showAttribute(orbID, 'noLocalCopies'), 'description': "Pass by reference", 'tagname': "noLocalCopies"});
  dataOut({'description': "Thread Pool", 'tagname': "threadpool", 'tagtype': "1"});
  orbTPID = cybcon_was.showAttribute(orbID, 'threadPool');
  if orbTPID == "":
    dataOut({'value': "No ORB thread pool defined."});
  else:
    dataOut({'name': "minimumSize", 'value': cybcon_was.showAttribute(orbTPID, 'minimumSize'), 'unit': "threads", 'description': "Minimum Size", 'tagname': "minimumSize"});
    dataOut({'name': "maximumSize", 'value': cybcon_was.showAttribute(orbTPID, 'maximumSize'), 'unit': "threads", 'description': "Maximum Size", 'tagname': "maximumSize"});
    dataOut({'name': "inactivityTimeout", 'value': cybcon_was.showAttribute(orbTPID, 'inactivityTimeout'), 'unit': "milliseconds", 'description': "Thread inactivity timeout", 'tagname': "inactivityTimeout"});
    dataOut({'name': "isGrowable", 'value': cybcon_was.showAttribute(orbTPID, 'isGrowable'), 'description': "Allow thread allocation beyond maximum thread size", 'tagname': "isGrowable"});
  dataOut({'tagname': "threadpool", 'tagtype': "2"});
  dataOut({'tagname': "orbservice", 'tagtype': "2"});

  dataOut({'description': "Startup Beans Service", 'tagname': "startupbeansservice", 'tagtype': "1"});
  dataOut({'name': "enable", 'value': cybcon_was.showAttribute(AdminConfig.list('StartupBeansService', serverID), 'enable'), 'description': "Enable service at server startup", 'tagname': "enable"});
  dataOut({'tagname': "startupbeansservice", 'tagtype': "2"});
  dataOut({'tagname': "containerservices", 'tagtype': "2"});
  dataOut({'tagname': "containersettings", 'tagtype': "2"});

  dataOut({'description': "Server Infrastructure", 'tagname': "serverinfrastructure", 'tagtype': "1"});
  dataOut({'description': "Administration", 'tagname': "administration", 'tagtype': "1"});
  dataOut({'description': "Custom properties", 'tagname': "customproperties", 'tagtype': "1"});
  CusProp="";
  for serverComponentID in AdminConfig.list('ApplicationServer', serverID).split(lineSeparator):
    for CusProp in cybcon_was.splitArray(cybcon_was.showAttribute(serverComponentID, 'properties')):
      dataOut({'name': "customProperty", 'value': cybcon_was.showAttribute(CusProp, 'value'), 'description': cybcon_was.showAttribute(CusProp, 'name'), 'tagname': "property"});
    if CusProp == "":
      dataOut({'value': "No custom properties set."});
  dataOut({'tagname': "customproperties", 'tagtype': "2"});
  dataOut({'tagname': "administration", 'tagtype': "2"});
  dataOut({'tagname': "serverinfrastructure", 'tagtype': "2"});

  dataOut({'description': "Additional Properties", 'tagname': "additionalproperties", 'tagtype': "1"});
  dataOut({'description': "Thread Pools", 'tagname': "threadpools", 'tagtype': "1"});
  ThreadPoolManagerID = AdminConfig.list('ThreadPoolManager', serverID);
  if ThreadPoolManagerID != "":
    for ThreadPoolID in cybcon_was.showAttribute(ThreadPoolManagerID, 'threadPools').split():
      ThreadPoolID = ThreadPoolID.replace("[", "").replace("]", "");
      if ThreadPoolID != "":
        dataOut({'tagname': "threadpool", 'tagtype': "1"});
        dataOut({'name': "name", 'value': cybcon_was.showAttribute(ThreadPoolID, 'name'), 'description': "Name", 'tagname': "name"});
        dataOut({'name': "description", 'value': cybcon_was.showAttribute(ThreadPoolID, 'description'), 'description': "Description", 'tagname': "description"});
        dataOut({'name': "minimumSize", 'value': cybcon_was.showAttribute(ThreadPoolID, 'minimumSize'), 'unit': "threads", 'description': "Minimum Size", 'tagname': "minimumSize"});
        dataOut({'name': "maximumSize", 'value': cybcon_was.showAttribute(ThreadPoolID, 'maximumSize'), 'unit': "threads", 'description': "Maximum Size", 'tagname': "maximumSize"});
        dataOut({'name': "inactivityTimeout", 'value': cybcon_was.showAttribute(ThreadPoolID, 'inactivityTimeout'), 'unit': "milliseconds", 'description': "Thread inactivity timeout", 'tagname': "inactivityTimeout"});
        dataOut({'name': "isGrowable", 'value': cybcon_was.showAttribute(ThreadPoolID, 'isGrowable'), 'description': "Allow thread allocation beyond maximum thread size", 'tagname': "isGrowable"});
        dataOut({'tagname': "threadpool", 'tagtype': "2"});
      else:
        dataOut({'value': "No thread pools defined in thread pool manager in this server."});
  else:
    dataOut({'value': "No thread pool manager defined in this server."});
  dataOut({'tagname': "threadpools", 'tagtype': "2"});
  dataOut({'tagname': "additionalproperties", 'tagtype': "2"});


#----------------------------------------------------------------------------
# get_JVMPropertiesFromServer
#   description: get the java and process menagement options from server
#   input: serverID
#   output: informations on stdout
#   return: -
#----------------------------------------------------------------------------
def get_JVMPropertiesFromServer(serverID):
  dataOut({'description': "Server Infrastructure", 'tagname': "serverinfrastructure", 'tagtype': "1"});
  dataOut({'description': "Java and Process Management", 'tagname': "javaandprocessmanagement", 'tagtype': "1"});

  dataOut({'description': "Class loaders", 'tagname': "classloaders", 'tagtype': "1"});
  ClassLoaderID="";
  for ClassLoaderID in AdminConfig.list('Classloader', serverID).split(lineSeparator):
    if ClassLoaderID != "":
      dataOut({'tagname': "classloader", 'tagtype': "1"});
      dataOut({'description': "Shared library references", 'tagname': "libraries", 'tagtype': "1"});
      ClassLoaderLibID="";
      for ClassLoaderLibID in cybcon_was.splitArray(cybcon_was.showAttribute(ClassLoaderID, 'libraries')):
        if ClassLoaderLibID != "":
          #dataOut({'tagname': "library", 'tagtype': "1"});
          dataOut({'name': "libraryName", 'value': cybcon_was.showAttribute(ClassLoaderLibID, 'libraryName'), 'description': "Library name", 'tagname': "libraryName"});
          #dataOut({'name': "sharedClassloader", 'value': cybcon_was.showAttribute(ClassLoaderLibID, 'sharedClassloader'), 'description': "Shared classloader", 'tagname': "sharedClassloader"});
          #dataOut({'tagname': "library", 'tagtype': "2"});
      if ClassLoaderLibID == "":
        dataOut({'value': "No Libraries defined"});
      dataOut({'tagname': "libraries", 'tagtype': "2"});
      dataOut({'name': "mode", 'value': cybcon_was.showAttribute(ClassLoaderID, 'mode'), 'description': "Class loader order", 'tagname': "mode"});
      dataOut({'tagname': "classloader", 'tagtype': "2"});
  if ClassLoaderID == "":
    dataOut({'value': "No Class loaders defined"});
  dataOut({'tagname': "classloaders", 'tagtype': "2"});

  dataOut({'description': "Process Definition", 'tagname': "processdefinition", 'tagtype': "1"});
  dataOut({'description': "Custom properties", 'tagname': "customproperties", 'tagtype': "1"});
  CusProp="";
  for CusProp in cybcon_was.splitArray(cybcon_was.showAttribute(AdminConfig.list('JavaProcessDef', serverID), 'environment')):
    dataOut({'name': "customProperty", 'value': cybcon_was.showAttribute(CusProp, 'value'), 'description': cybcon_was.showAttribute(CusProp, 'name'), 'tagname': "property"});
  if CusProp == "":
    dataOut({'value': "No custom properties set."});
  dataOut({'tagname': "customproperties", 'tagtype': "2"});

  dataOut({'description': "Java Virtual Machine", 'tagname': "javavirtualmachine", 'tagtype': "1"});
  jvmID = AdminConfig.list('JavaVirtualMachine', AdminConfig.list('JavaProcessDef', serverID));
  dataOut({'name': "classpath", 'value': cybcon_was.showAttribute(jvmID, 'classpath'), 'description': "Classpath", 'tagname': "classpath"});
  dataOut({'name': "bootClasspath", 'value': cybcon_was.showAttribute(jvmID, 'bootClasspath'), 'description': "Boot Classpath", 'tagname': "bootClasspath"});
  dataOut({'name': "verboseModeClass", 'value': cybcon_was.showAttribute(jvmID, 'verboseModeClass'), 'description': "Verbose class loading", 'tagname': "verboseModeClass"});
  dataOut({'name': "verboseModeGarbageCollection", 'value': cybcon_was.showAttribute(jvmID, 'verboseModeGarbageCollection'), 'description': "Verbose Garbage Collection", 'tagname': "verboseModeGarbageCollection"});
  dataOut({'name': "verboseModeJNI", 'value': cybcon_was.showAttribute(jvmID, 'verboseModeJNI'), 'description': "Verbose JNI", 'tagname': "verboseModeJNI"});
  dataOut({'name': "initialHeapSize", 'value': cybcon_was.showAttribute(jvmID, 'initialHeapSize'), 'description': "Initial Heap Size", 'tagname': "initialHeapSize"});
  dataOut({'name': "maximumHeapSize", 'value': cybcon_was.showAttribute(jvmID, 'maximumHeapSize'), 'description': "Maximum Heap Size", 'tagname': "maximumHeapSize"});
  dataOut({'name': "runHProf", 'value': cybcon_was.showAttribute(jvmID, 'runHProf'), 'description': "Run HProf", 'tagname': "runHProf"});
  dataOut({'name': "debugMode", 'value': cybcon_was.showAttribute(jvmID, 'debugMode'), 'description': "Debug Mode", 'tagname': "debugMode"});
  dataOut({'name': "debugArgs", 'value': cybcon_was.showAttribute(jvmID, 'debugArgs'), 'description': "Debug arguments", 'tagname': "debugArgs"});
  dataOut({'name': "genericJvmArguments", 'value': cybcon_was.showAttribute(jvmID, 'genericJvmArguments'), 'description': "Generic JVM arguments", 'tagname': "genericJvmArguments"});
  dataOut({'name': "disableJIT", 'value': cybcon_was.showAttribute(jvmID, 'disableJIT'), 'description': "Disable JIT", 'tagname': "disableJIT"});
  dataOut({'description': "Custom properties", 'tagname': "customproperties", 'tagtype': "1"});
  CusProp="";
  for CusProp in cybcon_was.splitArray(cybcon_was.showAttribute(jvmID, 'systemProperties')):
    dataOut({'name': "customProperty", 'value': cybcon_was.showAttribute(CusProp, 'value'), 'description': cybcon_was.showAttribute(CusProp, 'name'), 'tagname': "property"});
  if CusProp == "":
    dataOut({'value': "No custom properties set."});
  dataOut({'tagname': "customproperties", 'tagtype': "2"});
  dataOut({'tagname': "javavirtualmachine", 'tagtype': "2"});
  dataOut({'tagname': "processdefinition", 'tagtype': "2"});

  procExecID = cybcon_was.showAttribute(AdminConfig.list('JavaProcessDef', serverID), 'execution');
  dataOut({'description': "Process Execution", 'tagname': "processexecution", 'tagtype': "1"});
  dataOut({'name': "processPriority", 'value': cybcon_was.showAttribute(procExecID, 'processPriority'), 'description': "Process Priority", 'tagname': "processPriority"});
  dataOut({'name': "umask", 'value': cybcon_was.showAttribute(procExecID, 'umask'), 'description': "UMASK", 'tagname': "umask"});
  dataOut({'name': "runAsUser", 'value': cybcon_was.showAttribute(procExecID, 'runAsUser'), 'description': "Run As User", 'tagname': "runAsUser"});
  dataOut({'name': "runAsGroup", 'value': cybcon_was.showAttribute(procExecID, 'runAsGroup'), 'description': "Run As Group", 'tagname': "runAsGroup"});
  dataOut({'name': "runInProcessGroup", 'value': cybcon_was.showAttribute(procExecID, 'runInProcessGroup'), 'description': "Run In Process Group", 'tagname': "runInProcessGroup"});
  dataOut({'tagname': "processexecution", 'tagtype': "2"});

  dataOut({'description': "Monitoring Policy", 'tagname': "monitoringpolicy", 'tagtype': "1"});
  monitoringPolicyID = cybcon_was.showAttribute(AdminConfig.list('JavaProcessDef', serverID), 'monitoringPolicy');
  dataOut({'name': "maximumStartupAttempts", 'value': cybcon_was.showAttribute(monitoringPolicyID, 'maximumStartupAttempts'), 'unit': "attempts", 'description': "Maximum startup attempts", 'tagname': "maximumStartupAttempts"});
  dataOut({'name': "pingInterval", 'value': cybcon_was.showAttribute(monitoringPolicyID, 'pingInterval'), 'unit': "seconds", 'description': "Ping interval", 'tagname': "pingInterval"});
  dataOut({'name': "pingTimeout", 'value': cybcon_was.showAttribute(monitoringPolicyID, 'pingTimeout'), 'unit': "seconds", 'description': "Ping timeout", 'tagname': "pingTimeout"});
  dataOut({'name': "autoRestart", 'value': cybcon_was.showAttribute(monitoringPolicyID, 'autoRestart'), 'description': "Automatic restart", 'tagname': "autoRestart"});
  dataOut({'name': "nodeRestartState", 'value': cybcon_was.showAttribute(monitoringPolicyID, 'nodeRestartState'), 'description': "Node restart state", 'tagname': "nodeRestartState"});
  dataOut({'tagname': "monitoringpolicy", 'tagtype': "2"});

  dataOut({'tagname': "javaandprocessmanagement", 'tagtype': "2"});
  dataOut({'tagname': "serverinfrastructure", 'tagtype': "2"});

#----------------------------------------------------------------------------
# get_endPointPortsFromServer
#   description: searches all configured end point ports per server and
#     output them
#   input: serverEntryID
#   output: informations on stdout
#   return: -
#----------------------------------------------------------------------------
def get_endPointPortsFromServer(serverEntry):
  dataOut({'description': "Communications", 'tagname': "communications", 'tagtype': "1"});
  dataOut({'description': "Ports", 'tagname': "ports", 'tagtype': "1"});
  for namedEndPoint in AdminConfig.list("NamedEndPoint" , serverEntry).split(lineSeparator):
    endPoint = cybcon_was.showAttribute(namedEndPoint, "endPoint" );
    n = cybcon_was.showAttribute(namedEndPoint, "endPointName" );
    v = cybcon_was.showAttribute(endPoint, "port" );
    dataOut({'name': "NamedEndPoint", 'value': v, 'description': n, 'tagname': "NamedEndPoint"});
  dataOut({'tagname': "ports", 'tagtype': "2"});
  dataOut({'tagname': "communications", 'tagtype': "2"});


#----------------------------------------------------------------------------
# get_DCSTransportsFromServer
#   description: gets the Distribution and Consistency Services (DCS) messages
#     transport configuration
#   input: serverID
#   output: informations on stdout
#   return: -
#----------------------------------------------------------------------------
def get_DCSTransportsFromServer(serverID):
  dataOut({'description': "Distribution and Consistency Services (DCS) messages", 'tagname': "dcsmessages", 'tagtype': "1"});

  for tcsID in cybcon_was.splitArray(AdminConfig.list("TransportChannelService", serverID)):
    dataOut({'tagname': "TransportChannelService", 'tagtype': "1"});
    dataOut({'tagname': "chains", 'tagtype': "1"});
    for chainID in cybcon_was.splitArray(cybcon_was.showAttribute(tcsID, 'chains')):
      if chainID.startswith("DCS"):
        dataOut({'tagname': "chain", 'tagtype': "1"});
        dataOut({'name': "name", 'value': cybcon_was.showAttribute(chainID, 'name'), 'description': "Name", 'tagname': "name"});
        dataOut({'name': "enable", 'value': cybcon_was.showAttribute(chainID, 'enable'), 'description': "Enabled", 'tagname': "enable"});
        if cybcon_was.showAttribute(chainID, 'enable') == "true":
          dataOut({'description': "Transport Channels", 'tagname': "transportchannels", 'tagtype': "1"});
          for tranChanID in cybcon_was.splitArray(cybcon_was.showAttribute(chainID, 'transportChannels')):
            if tranChanID.startswith("TCP"):
              n = cybcon_was.showAttribute(tranChanID, 'name');
              dataOut({'description': "TCP Inbound Channel (" + n + ")", 'tagname': "transportchannel", 'tagtype': "1"});
              dataOut({'name': "name", 'value': n, 'description': "Name", 'tagname': "name"});
              dataOut({'name': "endPointName", 'value': cybcon_was.showAttribute(tranChanID, 'endPointName'), 'description': "Port", 'tagname': "endPointName"});
              threadPoolID = cybcon_was.showAttribute(tranChanID, 'threadPool');
              dataOut({'description': "Thread Pool", 'tagname': "threadpool", 'tagtype': "1"});
              if threadPoolID != "":
                dataOut({'name': "name", 'value': cybcon_was.showAttribute(threadPoolID, 'name'), 'description': "Name", 'tagname': "name"});
                dataOut({'name': "minimumSize", 'value': cybcon_was.showAttribute(threadPoolID, 'minimumSize'), 'unit': "threads", 'description': "Minimum Size", 'tagname': "minimumSize"});
                dataOut({'name': "maximumSize", 'value': cybcon_was.showAttribute(threadPoolID, 'maximumSize'), 'unit': "threads", 'description': "Maximum Size", 'tagname': "maximumSize"});
                dataOut({'name': "inactivityTimeout", 'value': cybcon_was.showAttribute(threadPoolID, 'inactivityTimeout'), 'unit': "milliseconds", 'description': "Thread inactivity timeout", 'tagname': "inactivityTimeout"});
                dataOut({'name': "isGrowable", 'value': cybcon_was.showAttribute(threadPoolID, 'isGrowable'), 'description': "Allow thread allocation beyond maximum thread size", 'tagname': "isGrowable"});
              dataOut({'tagname': "threadpool", 'tagtype': "2"});
              dataOut({'name': "maxOpenConnections", 'value': cybcon_was.showAttribute(tranChanID, 'maxOpenConnections'), 'description': "Maximum open connections", 'tagname': "maxOpenConnections"});
              dataOut({'name': "inactivityTimeout", 'value': cybcon_was.showAttribute(tranChanID, 'inactivityTimeout'), 'unit': "seconds", 'description': "Inactivity timeout", 'tagname': "inactivityTimeout"});
              dataOut({'name': "addressExcludeList", 'value': cybcon_was.showAttribute(tranChanID, 'addressExcludeList'), 'description': "Address exclude list", 'tagname': "addressExcludeList"});
              dataOut({'name': "addressIncludeList", 'value': cybcon_was.showAttribute(tranChanID, 'addressIncludeList'), 'description': "Address include list", 'tagname': "addressIncludeList"});
              dataOut({'name': "hostNameExcludeList", 'value': cybcon_was.showAttribute(tranChanID, 'hostNameExcludeList'), 'description': "Hostname exclude list", 'tagname': "hostNameExcludeList"});
              dataOut({'name': "hostNameIncludeList", 'value': cybcon_was.showAttribute(tranChanID, 'hostNameIncludeList'), 'description': "Hostname include list", 'tagname': "hostNameIncludeList"});
              dataOut({'description': "Custom properties", 'tagname': "customproperties", 'tagtype': "1"});
              CusProp="";
              for CusProp in cybcon_was.splitArray(cybcon_was.showAttribute(tranChanID, 'properties')):
                dataOut({'name': "customProperty", 'value': cybcon_was.showAttribute(CusProp, 'value'), 'description': cybcon_was.showAttribute(CusProp, 'name'), 'tagname': "property"});
              if CusProp == "":
                dataOut({'value': "No custom properties set."});
              dataOut({'tagname': "customproperties", 'tagtype': "2"});
              dataOut({'tagname': "transportchannel", 'tagtype': "2"});
            elif tranChanID.startswith("SSL"):
              n = cybcon_was.showAttribute(tranChanID, 'name');
              dataOut({'description': "SSL Inbound Channel (" + n + ")", 'tagname': "transportchannel", 'tagtype': "1"});
              dataOut({'name': "name", 'value': n, 'description': "Name", 'tagname': "name"});
              dataOut({'name': "discriminationWeight", 'value': cybcon_was.showAttribute(tranChanID, 'discriminationWeight'), 'description': "Discrimination weight", 'tagname': "discriminationWeight"});
              dataOut({'name': "sslConfigAlias", 'value': cybcon_was.showAttribute(tranChanID, 'sslConfigAlias'), 'description': "SSL repertoire", 'tagname': "sslConfigAlias"});
              dataOut({'description': "Custom properties", 'tagname': "customproperties", 'tagtype': "1"});
              CusProp="";
              for CusProp in cybcon_was.splitArray(cybcon_was.showAttribute(tranChanID, 'properties')):
                dataOut({'name': "customProperty", 'value': cybcon_was.showAttribute(CusProp, 'value'), 'description': cybcon_was.showAttribute(CusProp, 'name'), 'tagname': "property"});
              if CusProp == "":
                dataOut({'value': "No custom properties set."});
              dataOut({'tagname': "customproperties", 'tagtype': "2"});
              dataOut({'tagname': "transportchannel", 'tagtype': "2"});
            elif tranChanID.startswith("DCS"):
              n = cybcon_was.showAttribute(tranChanID, 'name');
              dataOut({'description': "Distribution and Consistency Services inbound channel (" + n + ")", 'tagname': "transportchannel", 'tagtype': "1"});
              dataOut({'name': "name", 'value': n, 'description': "Name", 'tagname': "name"});
              dataOut({'name': "discriminationWeight", 'value': cybcon_was.showAttribute(tranChanID, 'discriminationWeight'), 'description': "Discrimination weight", 'tagname': "discriminationWeight"});
              dataOut({'description': "Custom properties", 'tagname': "customproperties", 'tagtype': "1"});
              CusProp="";
              for CusProp in cybcon_was.splitArray(cybcon_was.showAttribute(tranChanID, 'properties')):
                dataOut({'name': "customProperty", 'value': cybcon_was.showAttribute(CusProp, 'value'), 'description': cybcon_was.showAttribute(CusProp, 'name'), 'tagname': "property"});
              if CusProp == "":
                dataOut({'value': "No custom properties set."});
              dataOut({'tagname': "customproperties", 'tagtype': "2"});
              dataOut({'tagname': "transportchannel", 'tagtype': "2"});
          dataOut({'tagname': "transportchannels", 'tagtype': "2"});
        dataOut({'tagname': "chain", 'tagtype': "2"});
    dataOut({'tagname': "chains", 'tagtype': "2"});
    dataOut({'tagname': "TransportChannelService", 'tagtype': "2"});

  dataOut({'tagname': "dcsmessages", 'tagtype': "2"});


#----------------------------------------------------------------------------
# get_MSGListenerServicePropertiesFromServer
#   description: output the relevant informations of listener ports
#   input: serverID, serverName
#   output: informations on stdout
#   return: -
#----------------------------------------------------------------------------
def get_MSGListenerServicePropertiesFromServer(serverID, serverName):
  dataOut({'description': "Messaging", 'tagname': "messaging", 'tagtype': "1"});
  dataOut({'description': "Message Listener Service", 'tagname': "messagelistenerservice", 'tagtype': "1"});
  dataOut({'description': "Listener Ports", 'tagname': "listenerports", 'tagtype': "1"});
  listenerPortFoundFlag="false";
  for listenerPortID in AdminConfig.list('ListenerPort', serverID).split(lineSeparator):
    if listenerPortID == "":
      dataOut({'value': "No message listener service defined for this server."});
      continue;
    listenerPortFoundFlag="true";
    dataOut({'tagname': "listenerport", 'tagtype': "1"});
    listenerPortName = cybcon_was.showAttribute(listenerPortID, 'name');
    dataOut({'name': "name", 'value': listenerPortName, 'description': "Name", 'tagname': "name"});
    dataOut({'name': "initialState", 'value': cybcon_was.showAttribute(cybcon_was.showAttribute(listenerPortID, 'stateManagement'), 'initialState'), 'description': "Initial State", 'tagname': "initialState"});
    listenerPortMBean = AdminControl.queryNames('type=ListenerPort,name=' + listenerPortName + ',process=' + serverName + ',*');
    if listenerPortMBean == "":
      dataOut({'name': "started", 'value': "unknown (no MBean found)", 'description': "Current State", 'tagname': "started"});
    else:
      listenerPortState = AdminControl.getAttribute(listenerPortMBean, 'started');
      if listenerPortState != "":
        dataOut({'name': "started", 'value': listenerPortState, 'description': "Current State", 'tagname': "started"});
      else:
        dataOut({'name': "started", 'value': "unknown (no state returned)", 'description': "Current State", 'tagname': "started"});
    dataOut({'name': "connectionFactoryJNDIName", 'value': cybcon_was.showAttribute(listenerPortID, 'connectionFactoryJNDIName'), 'description': "Connection factory JNDI name", 'tagname': "connectionFactoryJNDIName"});
    dataOut({'name': "destinationJNDIName", 'value': cybcon_was.showAttribute(listenerPortID, 'destinationJNDIName'), 'description': "Destination JNDI name", 'tagname': "destinationJNDIName"});
    dataOut({'name': "maxSessions", 'value': cybcon_was.showAttribute(listenerPortID, 'maxSessions'), 'description': "Maximum sessions", 'tagname': "maxSessions"});
    dataOut({'name': "maxRetries", 'value': cybcon_was.showAttribute(listenerPortID, 'maxRetries'), 'description': "Maximum retries", 'tagname': "maxRetries"});
    dataOut({'name': "maxMessages", 'value': cybcon_was.showAttribute(listenerPortID, 'maxMessages'), 'description': "Maximum messages", 'tagname': "maxMessages"});
    dataOut({'tagname': "listenerport", 'tagtype': "2"});
  dataOut({'tagname': "listenerports", 'tagtype': "2"});

  if listenerPortFoundFlag == "true":
    dataOut({'description': "Thread Pool", 'tagname': "threadpool", 'tagtype': "1"});
    threadPoolName = AdminControl.completeObjectName('type=ThreadPool,name=MessageListenerThreadPool,process=' + serverName + ',*');
    if threadPoolName != "":
      threadPoolID = AdminControl.getConfigId(threadPoolName);
    else:
      threadPoolID = "";
    if threadPoolID == "":
      dataOut({'value': "No thread pool found."});
    else:
      dataOut({'name': "minimumSize", 'value': cybcon_was.showAttribute(threadPoolID, 'minimumSize'), 'unit': "threads", 'description': "Minimum Size", 'tagname': "minimumSize"});
      dataOut({'name': "maximumSize", 'value': cybcon_was.showAttribute(threadPoolID, 'maximumSize'), 'unit': "threads", 'description': "Maximum Size", 'tagname': "maximumSize"});
      dataOut({'name': "inactivityTimeout", 'value': cybcon_was.showAttribute(threadPoolID, 'inactivityTimeout'), 'unit': "milliseconds", 'description': "Thread inactivity timeout", 'tagname': "inactivityTimeout"});
      dataOut({'name': "isGrowable", 'value': cybcon_was.showAttribute(threadPoolID, 'isGrowable'), 'description': "Allow thread allocation beyond maximum thread size", 'tagname': "isGrowable"});
    dataOut({'tagname': "threadpool", 'tagtype': "2"});

    for MSGListenerSrvID in AdminConfig.list('MessageListenerService', serverID).split(lineSeparator):
      dataOut({'description': "Custom properties", 'tagname': "customproperties", 'tagtype': "1"});
      CusProp="";
      for CusProp in cybcon_was.splitArray(cybcon_was.showAttribute(MSGListenerSrvID, 'properties')):
        dataOut({'name': "customProperty", 'value': cybcon_was.showAttribute(CusProp, 'value'), 'description': cybcon_was.showAttribute(CusProp, 'name'), 'tagname': "property"});
      if CusProp == "":
        dataOut({'value': "No custom properties set."});
      dataOut({'tagname': "customproperties", 'tagtype': "2"});
  dataOut({'tagname': "messagelistenerservice", 'tagtype': "2"});
  dataOut({'tagname': "messaging", 'tagtype': "2"});

#----------------------------------------------------------------------------
# get_HAManagerServiceProperties
#   description: output the relevant informations of the High Availability
#     Manager Service
#   input: serverID
#   output: informations on stdout
#   return: -
#----------------------------------------------------------------------------
def get_HAManagerServiceProperties(serverID):
  dataOut({'description': "Additional Properties", 'tagname': "additionalproperties", 'tagtype': "1"});
  dataOut({'description': "Core group service", 'tagname': "coregroupservice", 'tagtype': "1"});

  for HAManSrvID in cybcon_was.splitArray(AdminConfig.list("HAManagerService", serverID)):
    dataOut({'tagname': "HAManagerService", 'tagtype': "1"});
    dataOut({'name': "enable", 'value': cybcon_was.showAttribute(HAManSrvID, 'enable'), 'description': "Enable service at server startup", 'tagname': "enable"});
    dataOut({'name': "coreGroupName", 'value': cybcon_was.showAttribute(HAManSrvID, 'coreGroupName'), 'description': "Core group name", 'tagname': "coreGroupName"});
    dataOut({'name': "activateEnabled", 'value': cybcon_was.showAttribute(HAManSrvID, 'activateEnabled'), 'description': "Allow activation", 'tagname': "activateEnabled"});
    dataOut({'name': "isAlivePeriodSec", 'value': cybcon_was.showAttribute(HAManSrvID, 'isAlivePeriodSec'), 'unit': "seconds", 'description': "Is alive timer", 'tagname': "isAlivePeriodSec"});
    dataOut({'name': "transportBufferSize", 'value': cybcon_was.showAttribute(HAManSrvID, 'transportBufferSize'), 'unit': "MB", 'description': "Transport buffer size", 'tagname': "transportBufferSize"});
    dataOut({'tagname': "HAManagerService", 'tagtype': "2"});

  dataOut({'tagname': "coregroupservice", 'tagtype': "2"});
  dataOut({'tagname': "additionalproperties", 'tagtype': "2"});

#----------------------------------------------------------------------------
# get_troubleshootingProperties
#   description: output the logfile specifications
#   input: serverID
#   output: informations on stdout
#   return: -
#----------------------------------------------------------------------------
def get_troubleshootingProperties(serverID):
  dataOut({'description': "Troubleshooting", 'tagname': "troubleshooting", 'tagtype': "1"});
  dataOut({'description': "Logging and Tracing", 'tagname': "loggingandtracing", 'tagtype': "1"});

  dataOut({'description': "Diagnostic Trace", 'tagname': "diagnostictrace", 'tagtype': "1"});
  for traceServiceID in AdminConfig.list('TraceService', serverID).split(lineSeparator):
    dataOut({'name': "enable", 'value': cybcon_was.showAttribute(traceServiceID, 'enable'), 'description': "Enable Log", 'tagname': "enable"});
    if cybcon_was.showAttribute(traceServiceID, 'traceOutputType').find("SPECIFIED_FILE") != -1:
      dataOut({'name': "traceOutputType", 'value': "File", 'description': "Trace Output", 'tagname': "traceoutputtype"});
      traceServiceFileID = cybcon_was.showAttribute(traceServiceID, 'traceLog');
      if traceServiceFileID != "":
        dataOut({'name': "rolloverSize", 'value': cybcon_was.showAttribute(traceServiceFileID, 'rolloverSize'), 'unit': "MB", 'description': "Maximum File Size", 'tagname': "rolloverSize"});
        dataOut({'name': "maxNumberOfBackupFiles", 'value': cybcon_was.showAttribute(traceServiceFileID, 'maxNumberOfBackupFiles'), 'description': "Maximum Number of Historical Files", 'tagname': "maxNumberOfBackupFiles"});
        dataOut({'name': "fileName", 'value': cybcon_was.showAttribute(traceServiceFileID, 'fileName'), 'description': "File Name", 'tagname': "fileName"});
      else:
        dataOut({'description': "WARNING", 'value': "no trace file specified!"});
    else:
      dataOut({'name': "traceOutputType", 'value': "Memory Buffer", 'description': "Trace Output", 'tagname': "traceoutputtype"});
      dataOut({'name': "memoryBufferSize", 'value': cybcon_was.showAttribute(traceServiceID, 'memoryBufferSize'), 'unit': "thousand entries", 'description': "Maximum Buffer Size", 'tagname': "memoryBufferSize"});
    dataOut({'name': "traceFormat", 'value': cybcon_was.showAttribute(traceServiceID, 'traceFormat'), 'description': "Trace Output Format", 'tagname': "traceFormat"});
    dataOut({'name': "startupTraceSpecification", 'value': cybcon_was.showAttribute(traceServiceID, 'startupTraceSpecification'), 'description': "Log Detail Levels", 'tagname': "startupTraceSpecification"});
  dataOut({'tagname': "diagnostictrace", 'tagtype': "2"});

  dataOut({'description': "JVM Logs", 'tagname': "jvmlogs", 'tagtype': "1"});
  jvmlogtypes = [ "outputStreamRedirect", "errorStreamRedirect" ];
  for jvmlogtype in jvmlogtypes:
    if jvmlogtype == "outputStreamRedirect":
      dataOut({'description': "System.out", 'tagname': "systemout", 'tagtype': "1"});
    elif jvmlogtype == "errorStreamRedirect":
      dataOut({'description': "System.err", 'tagname': "systemerr", 'tagtype': "1"});

    streamRedirectID = cybcon_was.showAttribute(serverID, jvmlogtype);
    dataOut({'name': "fileName", 'value': cybcon_was.showAttribute(streamRedirectID, 'fileName'), 'description': "File Name", 'tagname': "fileName"});
    dataOut({'name': "messageFormatKind", 'value': cybcon_was.showAttribute(streamRedirectID, 'messageFormatKind'), 'description': "File Formatting", 'tagname': "messageFormatKind"});
    dataOut({'description': "Log File Rotation", 'tagname': "logfilerotation", 'tagtype': "1"});
    # rotate by Size
    if cybcon_was.showAttribute(streamRedirectID, 'rolloverType').lower().find("size") != -1 or cybcon_was.showAttribute(streamRedirectID, 'rolloverType').lower().find("both") != -1:
      dataOut({'name': "rolloverType", 'value': "true", 'description': "Rotate by file size", 'tagname': "rolloverTypeSize"});
    else:
      dataOut({'name': "rolloverType", 'value': "false", 'description': "Rotate by file size", 'tagname': "rolloverTypeSize"});
    dataOut({'name': "rolloverSize", 'value': cybcon_was.showAttribute(streamRedirectID, 'rolloverSize'), 'unit': "MB", 'description': "Maximum Size", 'tagname': "rolloverSize"});

    # rotate by Time
    if cybcon_was.showAttribute(streamRedirectID, 'rolloverType').lower().find("time") != -1 or cybcon_was.showAttribute(streamRedirectID, 'rolloverType').lower().find("both") != -1:
      dataOut({'name': "rolloverType", 'value': "true", 'description': "Rotate by time", 'tagname': "rolloverTypeTime"});
    else:
      dataOut({'name': "rolloverType", 'value': "false", 'description': "Rotate by time", 'tagname': "rolloverTypeTime"});
    dataOut({'name': "baseHour", 'value': cybcon_was.showAttribute(streamRedirectID, 'baseHour'), 'description': "Start Time", 'tagname': "baseHour"});
    dataOut({'name': "rolloverPeriod", 'value': cybcon_was.showAttribute(streamRedirectID, 'rolloverPeriod'), 'unit': "hours", 'description': "Repeat Time", 'tagname': "rolloverPeriod"});
    dataOut({'tagname': "logfilerotation", 'tagtype': "2"});
    dataOut({'name': "maxNumberOfBackupFiles", 'value': cybcon_was.showAttribute(streamRedirectID, 'maxNumberOfBackupFiles'), 'description': "Maximum Number of Historical Log Files", 'tagname': "maxNumberOfBackupFiles"});
    dataOut({'description': "Installed Application Output", 'tagname': "installedapplicationoutput", 'tagtype': "1"});
    dataOut({'description': "Show application print statements", 'tagname': "showapplicationprintstatements", 'tagtype': "1"});
    dataOut({'name': "suppressStackTrace", 'value': cybcon_was.showAttribute(streamRedirectID, 'suppressStackTrace'), 'description': "Suppress Stack Trace", 'tagname': "suppressStackTrace"});
    dataOut({'name': "suppressWrites", 'value': cybcon_was.showAttribute(streamRedirectID, 'suppressWrites'), 'description': "Suppress Writes", 'tagname': "suppressWrites"});
    dataOut({'name': "formatWrites", 'value': cybcon_was.showAttribute(streamRedirectID, 'formatWrites'), 'description': "Format print statements", 'tagname': "formatWrites"});
    dataOut({'tagname': "showapplicationprintstatements", 'tagtype': "2"});
    dataOut({'tagname': "installedapplicationoutput", 'tagtype': "2"});

    if jvmlogtype == "outputStreamRedirect":
      dataOut({'tagname': "systemout", 'tagtype': "2"});
    elif jvmlogtype == "errorStreamRedirect":
      dataOut({'tagname': "systemerr", 'tagtype': "2"});

  dataOut({'tagname': "jvmlogs", 'tagtype': "2"});

  dataOut({'description': "IBM Service Logs", 'tagname': "serviceLog", 'tagtype': "1"});
  serviceLogID = AdminConfig.list('ServiceLog', serverID);
  if serviceLogID != '':
    dataOut({'name': "enable", 'value': cybcon_was.showAttribute(serviceLogID, 'enabled'), 'description': "Enable service log", 'tagname': "enable"});
    dataOut({'name': "fileName", 'value': cybcon_was.showAttribute(serviceLogID, 'name'), 'description': "File Name", 'tagname': "fileName"});
    dataOut({'name': "size", 'value': cybcon_was.showAttribute(serviceLogID, 'size'), 'unit': "MB", 'description': "Maximum File Size", 'tagname': "size"});
  dataOut({'tagname': "serviceLog", 'tagtype': "2"});

  dataOut({'tagname': "loggingandtracing", 'tagtype': "2"});
  dataOut({'tagname': "troubleshooting", 'tagtype': "2"});

#----------------------------------------------------------------------------
# get_SIBusProperties
#   description: output the service integration bus specifications
#   input: cellID
#   output: informations on stdout
#   return: -
#----------------------------------------------------------------------------
def get_SIBusProperties(cellID):
  dataOut({'description': "Service integration", 'tagname': "serviceintegration", 'tagtype': "1"});
  dataOut({'description': "Buses", 'tagname': "buses", 'tagtype': "1"});
  
  for SIBusID in AdminConfig.list('SIBus', cellID).split(lineSeparator):
    if SIBusID != "":
      dataOut({'tagname': "sibus", 'tagtype': "1"});
      dataOut({'name': "name", 'value': cybcon_was.showAttribute(SIBusID, 'name'), 'description': "Name", 'tagname': "name"});
      dataOut({'name': "uuid", 'value': cybcon_was.showAttribute(SIBusID, 'uuid'), 'description': "UUID", 'tagname': "uuid"});
      dataOut({'name': "permittedChains", 'value': cybcon_was.showAttribute(SIBusID, 'permittedChains'), 'description': "Inter-engine transport chain", 'tagname': "permittedChains"});
      dataOut({'name': "discardMsgsAfterQueueDeletion", 'value': cybcon_was.showAttribute(SIBusID, 'discardMsgsAfterQueueDeletion'), 'description': "Discard messages", 'tagname': "discardMsgsAfterQueueDeletion"});
      dataOut({'name': "configurationReloadEnabled", 'value': cybcon_was.showAttribute(SIBusID, 'configurationReloadEnabled'), 'description': "Configuration reload enabled", 'tagname': "configurationReloadEnabled"});
      dataOut({'name': "highMessageThreshold", 'value': cybcon_was.showAttribute(SIBusID, 'highMessageThreshold'), 'unit': "messages", 'description': "High message threshold", 'tagname': "highMessageThreshold"});

      dataOut({'description': "Messaging engines", 'tagname': "messagingengines", 'tagtype': "1"});
      for SIBMsgID in AdminConfig.list('SIBMessagingEngine', cellID).split(lineSeparator):
        if SIBMsgID != "":
          dataOut({'tagname': "messagingengine", 'tagtype': "1"});
          if cybcon_was.showAttribute(SIBusID, 'uuid') == cybcon_was.showAttribute(SIBMsgID, 'busUuid'):
            dataOut({'name': "name", 'value': cybcon_was.showAttribute(SIBMsgID, 'name'), 'description': "Name", 'tagname': "name"});
            dataOut({'name': "uuid", 'value': cybcon_was.showAttribute(SIBMsgID, 'uuid'), 'description': "UUID", 'tagname': "uuid"});
            dataOut({'name': "initialState", 'value': cybcon_was.showAttribute(SIBMsgID, 'initialState'), 'description': "Initial state", 'tagname': "initialState"});
            dataOut({'name': "messageStoreType", 'value': cybcon_was.showAttribute(SIBMsgID, 'messageStoreType'), 'description': "Message store type", 'tagname': "messageStoreType"});
            dataOut({'name': "highMessageThreshold", 'value': cybcon_was.showAttribute(SIBMsgID, 'highMessageThreshold'), 'unit': "messages", 'description': "High message threshold", 'tagname': "highMessageThreshold"});
            dataOut({'name': "busName", 'value': cybcon_was.showAttribute(SIBMsgID, 'busName'), 'description': "Bus name", 'tagname': "busName"});
            dataOut({'name': "busUuid", 'value': cybcon_was.showAttribute(SIBMsgID, 'busUuid'), 'description': "Bus UUID", 'tagname': "busUuid"});

            dataOut({'description': "Additional Properties", 'tagname': "additionalproperties", 'tagtype': "1"});
            SIBMsgIDDS = cybcon_was.showAttribute(SIBMsgID, 'dataStore');
            dataOut({'description': "Data store", 'tagname': "datastore", 'tagtype': "1"});
            if SIBMsgIDDS != "":
              dataOut({'name': "uuid", 'value': cybcon_was.showAttribute(SIBMsgIDDS, 'uuid'), 'description': "UUID", 'tagname': "uuid"});
              dataOut({'name': "dataSourceName", 'value': cybcon_was.showAttribute(SIBMsgIDDS, 'dataSourceName'), 'description': "Data source JNDI name", 'tagname': "dataSourceName"});
              dataOut({'name': "schemaName", 'value': cybcon_was.showAttribute(SIBMsgIDDS, 'schemaName'), 'description': "Schema name", 'tagname': "schemaName"});
              dataOut({'name': "createTables", 'value': cybcon_was.showAttribute(SIBMsgIDDS, 'createTables'), 'description': "Create tables", 'tagname': "createTables"});
            else:
              dataOut({'value': "No Data store defined for this messaging engine."});
            dataOut({'tagname': "datastore", 'tagtype': "2"});

            # The mediations thread pool, attribute name mediationsThreadPool, is an attribute of the messaging engine.
            # By default, mediationsThreadPool does not exist, and a default thread pool is created and used at runtime.
            # http://publib.boulder.ibm.com/infocenter/wasinfo/v6r1/index.jsp?topic=/com.ibm.websphere.pmc.express.doc/ref/rjp0040_.html
            medThreadPoolID = cybcon_was.showAttribute(SIBMsgID, 'mediationsThreadPool');
            dataOut({'description': "Mediation thread pool", 'tagname': "mediationthreadpool", 'tagtype': "1"});
            if medThreadPoolID != "":
              dataOut({'name': "minimumSize", 'value': cybcon_was.showAttribute(medThreadPoolID, 'minimumSize'), 'description': "Minimum size", 'tagname': "minimumSize"});
              dataOut({'name': "maximumSize", 'value': cybcon_was.showAttribute(medThreadPoolID, 'maximumSize'), 'description': "Maximum size", 'tagname': "maximumSize"});
              dataOut({'name': "inactivityTimeout", 'value': cybcon_was.showAttribute(medThreadPoolID, 'inactivityTimeout'), 'unit': "milliseconds", 'description': "Thread inactivity timeout", 'tagname': "inactivityTimeout"});
              dataOut({'name': "isGrowable", 'value': cybcon_was.showAttribute(medThreadPoolID, 'isGrowable'), 'description': "Allow thread allocation beyond maximum thread pool size", 'tagname': "isGrowable"});
            else:
              dataOut({'value': "No mediation thread pool exists - this is the default."});
              dataOut({'value': "If mediation thread pool not exist, a default thread pool is used."});
              dataOut({'value': "Default thread pool properties (as documented in internet):"});
              # output the default thread pool
              dataOut({'description': "Minimum size", 'value': "1"});
              dataOut({'description': "Maximum size", 'value': "5"});
              dataOut({'description': "Thread inactivity timeout", 'value': "3500", 'unit': "milliseconds"});
              dataOut({'description': "Allow thread allocation beyond maximum thread pool size", 'value': "false"});
            dataOut({'tagname': "mediationthreadpool", 'tagtype': "2"});
            dataOut({'tagname': "additionalproperties", 'tagtype': "2"});
          dataOut({'tagname': "messagingengine", 'tagtype': "2"});
        else:
          dataOut({'value': "No messaging engine defined for this bus."});
      dataOut({'tagname': "messagingengines", 'tagtype': "2"});
      dataOut({'tagname': "sibus", 'tagtype': "2"});
    else:
      dataOut({'value': "No buses defined."});
  dataOut({'tagname': "buses", 'tagtype': "2"});
  dataOut({'tagname': "serviceintegration", 'tagtype': "2"});


#----------------------------------------------------------------------------
# get_serviceProviders
#   description: output the service provider informations
#   input: -
#   output: informations on stdout
#   return: -
#----------------------------------------------------------------------------
def get_serviceProviders():
  dataOut({'description': "Service providers", 'tagname': "serviceproviders", 'tagtype': "1"});

  # Attribute list of WebServices
  webServiceAttrList=['service', 'client', 'application', 'module', 'type' ];
  # Attribute list of Policy set attachments
  psaAttrList=['policySet', 'resource', 'attachmentId', 'directAttachment', 'binding' ];

  # loop over webservices
  try:
    for webService in AdminTask.listWebServices().split(lineSeparator):
      if webService != "":
        webService = webService.replace("[ [", "").replace("] ]", "");
        # generate empty webService dictionary
        wsDict = {};
        for wsAttribute in webServiceAttrList:
          wsDict[wsAttribute] = "";

        # loop over attribute lines
        for webServiceAttribute in webService.split('] ['):
          for wsAttribute in webServiceAttrList:
            wsAtLen=len(wsAttribute);
            if webServiceAttribute[:wsAtLen].find(wsAttribute) != -1:
              wsDict[wsAttribute] = webServiceAttribute[wsAtLen:].strip();
              continue;
  
        #output informations:
        if wsDict['service'] != "":
          dataOut({'tagname': "serviceprovider", 'tagtype': "1"});
          name = wsDict['service'].split('}')[1];
          dataOut({'name': 'name', 'value': name, 'description': 'Name', 'tagname': 'name'});
          dataOut({'name': 'service', 'value': wsDict['service'], 'description': 'Service provider', 'tagname': 'service'});
          dataOut({'name': 'type', 'value': wsDict['type'], 'description': 'Type', 'tagname': 'type'});
          dataOut({'name': 'application', 'value': wsDict['application'], 'description': 'Application', 'tagname': 'application'});
          dataOut({'name': 'module', 'value': wsDict['module'], 'description': 'Module', 'tagname': 'module'});
          dataOut({'name': 'client', 'value': wsDict['client'], 'description': 'Client', 'tagname': 'client'});
          dataOut({'description': "Policy set attachments", 'tagname': "policysetattachments", 'tagtype': "1"});

          # loop over Policy set attachments for the given webservice
          if wsDict['application'] != "":
            for psa in AdminTask.getPolicySetAttachments('[-applicationName ' + wsDict['application'] + ' -attachmentType application -expandResources ' + wsDict['service'] + ']').split(lineSeparator):
              if psa != "":
                psa = psa.replace("[ [", "").replace("] ]", "");
                # generate empty policy set attachment dictionary
                psaDict = {};
                for psaAttribute in psaAttrList:
                  psaDict[psaAttribute] = "";

                # loop over attribute lines
                for psaAtVal in psa.split('] ['):
                  for psaAttribute in psaAttrList:
                    psaAtLen=len(psaAttribute);
                    if psaAtVal[:psaAtLen].find(psaAttribute) != -1:
                      psaDict[psaAttribute] = psaAtVal[psaAtLen:].replace('[', "").replace(']', "").strip();
                      continue;
  
                #output informations:
                if psaDict['resource'] != "":
                  dataOut({'tagname': "policysetattachment", 'tagtype': "1"});
                  #res=psaDict['resource'].split('}')[-1].split('/')[-1];
                  res=psaDict['resource'].split('}')[-1];
                  dataOut({'name': 'resource', 'value': res, 'description': 'Service/Endpoint/Operation', 'tagname': 'resource'});
                  #if psaDict['policySet'] == "": psaDict['policySet'] = "None";
                  dataOut({'name': 'policySet', 'value': psaDict['policySet'], 'description': 'Attached policy set', 'tagname': 'policySet'});
                  #if psaDict['binding'] == "": psaDict['binding'] = "Not applicable";
                  dataOut({'name': 'binding', 'value': psaDict['binding'], 'description': 'Binding', 'tagname': 'binding'});
                  #if psaDict['directAttachment'] == "true":
                  #  dataOut({'description': 'Binding policies', 'tagname': "bindingpolicies", 'tagtype': "1"});
                  #  for policyType in AdminTask.listPolicyTypes('[-bindingLocation "[ [application ' + wsDict['application'] + '] [attachmentId ' + psaDict['attachmentId'] + '] ]" -attachmentType application]'):
                  #    dataOut({'tagname': "bindingpolicy", 'tagtype': "1"});
                  #    dataOut({'name': 'policyType', 'value': policyType, 'description': 'Policy', 'tagname': 'policyType'});
                  #    dataOut({'tagname': "bindingpolicy", 'tagtype': "2"});
                  #  dataOut({'tagname': "bindingpolicies", 'tagtype': "2"});
                  #dataOut({'name': 'directAttachment', 'value': psaDict['directAttachment'], 'description': 'Direct Attachment', 'tagname': 'directAttachment'});
                  #dataOut({'name': 'attachmentId', 'value': psaDict['attachmentId'], 'description': 'Attachment ID', 'tagname': 'attachmentId'});
                  dataOut({'tagname': "policysetattachment", 'tagtype': "2"});
                else:
                  dataOut({'value': "No policy set attachment in webservice."});
              else:
                dataOut({'value': "No policy set attachment in webservice."});
            else:
              dataOut({'value': "No application available to have policy set attachments in webservice."});
          dataOut({'tagname': "policysetattachments", 'tagtype': "2"});
          dataOut({'tagname': "serviceprovider", 'tagtype': "2"});
        else:
          dataOut({'value': "No service provider defined."});
      else:
        dataOut({'value': "No service provider defined."});
  except AttributeError:
    dataOut({'description': "WARNING", 'value': "The Server not supports AdminTask.listWebServices().", 'tagname': "WARNING"});

  dataOut({'tagname': "serviceproviders", 'tagtype': "2"});

#----------------------------------------------------------------------------
# get_ApplicationPolicySets
#   description: output the application policy sets
#   input: -
#   output: informations on stdout
#   return: -
#----------------------------------------------------------------------------
def get_ApplicationPolicySets():
  dataOut({'description': "Policy sets", 'tagname': "policysets", 'tagtype': "1"});
  dataOut({'description': "Application policy sets", 'tagname': "apppolicysets", 'tagtype': "1"});

  try:
    for PolicySet in AdminTask.listPolicySets().split(lineSeparator):
      dataOut({'name': "PolicySet", 'value': PolicySet, 'description': "Name", 'tagname': "policyset"});
      dataOut({'description': "Attached applications", 'tagname': "attachedapplications", 'tagtype': "1"});
      for PolicyAttachment in AdminTask.listAttachmentsForPolicySet(['-policySet "' + PolicySet +'"']).split(lineSeparator):
        if PolicyAttachment == "": PolicyAttachment="No Application attached";
        dataOut({'value': PolicyAttachment, 'tagname': "policyattachment"});
      dataOut({'tagname': "attachedapplications", 'tagtype': "2"});
      dataOut({'description': "Policies", 'tagname': "policies", 'tagtype': "1"});
      for PolicyType in AdminTask.listPolicyTypes(['-policySet "' + PolicySet +'"']).split(lineSeparator):
        dataOut({'value': PolicyType, 'tagname': "policytype"});
      dataOut({'tagname': "policies", 'tagtype': "2"});
  except AttributeError:
    dataOut({'description': "WARNING", 'value': "The Server not supports AdminTask.listPolicySets().", 'tagname': "WARNING"});
  except NameError:
    dataOut({'description': "WARNING", 'value': "The Server not supports AdminTask.", 'tagname': "WARNING"});
  dataOut({'tagname': "apppolicysets", 'tagtype': "2"});
  dataOut({'tagname': "policysets", 'tagtype': "2"});

#----------------------------------------------------------------------------
# get_AsyncBeans
#   description: output the configured asynchroneous beans on the given
#     objectID level
#   input: objectID (can be cellID, clusterID, nodeID or serverID)
#   output: informations on stdout
#   return: -
#----------------------------------------------------------------------------
def get_AsyncBeans(objectID):
  dataOut({'description': "Asynchronous beans", 'tagname': "asyncbeans", 'tagtype': "1"});
# get name and objectType of the objectID
  objectName = cybcon_was.showAttribute(objectID, 'name');
  objectType = cybcon_was.get_ObjectTypeByID(objectID);
  if objectType == "Server":
    nodeName = cybcon_was.get_nodeNameByServerID(objectID);
    if nodeName != "": objectType = 'Node:' + nodeName + '/' + objectType;

  dataOut({'description': "Timer managers", 'tagname': "timermanagers", 'tagtype': "1"});
# get IDs, searching by scope, and type
  for TMID in AdminConfig.getid('/' + objectType + ':' + objectName + '/TimerManagerProvider:TimerManagerProvider/TimerManagerInfo:/').split(lineSeparator):
    if TMID != "":
      dataOut({'tagname': "timermanager", 'tagtype': "1"});
      dataOut({'name': "name", 'value': cybcon_was.showAttribute(TMID, 'name'), 'description': "Name", 'tagname': "name"});
      dataOut({'name': "jndiName", 'value': cybcon_was.showAttribute(TMID, 'jndiName'), 'description': "JNDI name", 'tagname': "jndiName"});
      dataOut({'name': "description", 'value': cybcon_was.showAttribute(TMID, 'description'), 'description': "Description", 'tagname': "description"});
      dataOut({'name': "category", 'value': cybcon_was.showAttribute(TMID, 'category'), 'description': "Category", 'tagname': "category"});

      dataOut({'description': "Service names", 'tagname': "servicenames", 'tagtype': "1"});
      if cybcon_was.showAttribute(TMID, 'serviceNames').lower().find("zos.wlm") != -1:
        dataOut({'name': "serviceName", 'value': "true", 'description': "z/OS WLM Service Class", 'tagname': "servicename"});
      else:
        dataOut({'name': "serviceName", 'value': "false", 'description': "z/OS WLM Service Class", 'tagname': "servicename"});
      if cybcon_was.showAttribute(TMID, 'serviceNames').lower().find("userworkarea") != -1:
        dataOut({'name': "serviceName", 'value': "true", 'description': "WorkArea", 'tagname': "servicename"});
      else:
        dataOut({'name': "serviceName", 'value': "false", 'description': "WorkArea", 'tagname': "servicename"});
      if cybcon_was.showAttribute(TMID, 'serviceNames').lower().find("security") != -1:
        dataOut({'name': "serviceName", 'value': "true", 'description': "Security", 'tagname': "servicename"});
      else:
        dataOut({'name': "serviceName", 'value': "false", 'description': "Security", 'tagname': "servicename"});
      if cybcon_was.showAttribute(TMID, 'serviceNames').lower().find("com.ibm.ws.i18n") != -1:
        dataOut({'name': "serviceName", 'value': "true", 'description': "Internationalization", 'tagname': "servicename"});
      else:
        dataOut({'name': "serviceName", 'value': "false", 'description': "Internationalization", 'tagname': "servicename"});
      dataOut({'tagname': "servicenames", 'tagtype': "2"});

      dataOut({'description': "Thread pool properties", 'tagname': "threadpoolproperties", 'tagtype': "1"});
      dataOut({'name': "numAlarmThreads", 'value': cybcon_was.showAttribute(TMID, 'numAlarmThreads'), 'unit': "threads", 'description': "Number of timer threads", 'tagname': "numalarmthreads"});
      dataOut({'tagname': "threadpoolproperties", 'tagtype': "2"});

      dataOut({'description': "Custom properties", 'tagname': "customproperties", 'tagtype': "1"});
      CusProp="";
      for CusProp in cybcon_was.splitArray(cybcon_was.showAttribute(TMID, 'customProperties')):
        dataOut({'name': "customProperty", 'value': cybcon_was.showAttribute(CusProp, 'value'), 'description': cybcon_was.showAttribute(CusProp, 'name'), 'tagname': "property"});
      if CusProp == "":
        dataOut({'value': "No custom properties set."});
      dataOut({'tagname': "customproperties", 'tagtype': "2"});

      dataOut({'tagname': "timermanager", 'tagtype': "2"});
    else:
      dataOut({'value': "No timer managers configured on this scope."});
  dataOut({'tagname': "timermanagers", 'tagtype': "2"});

  dataOut({'description': "Work managers", 'tagname': "workmanagers", 'tagtype': "1"});
# get IDs, searching by scope, and type
  for WMID in AdminConfig.getid('/' + objectType + ':' + objectName + '/WorkManagerProvider:WorkManagerProvider/WorkManagerInfo:/').split(lineSeparator):
    if WMID != "":
      dataOut({'tagname': "workmanager", 'tagtype': "1"});
      dataOut({'name': "name", 'value': cybcon_was.showAttribute(WMID, 'name'), 'description': "Name", 'tagname': "name"});
      dataOut({'name': "jndiName", 'value': cybcon_was.showAttribute(WMID, 'jndiName'), 'description': "JNDI name", 'tagname': "jndiName"});
      dataOut({'name': "description", 'value': cybcon_was.showAttribute(WMID, 'description'), 'description': "Description", 'tagname': "description"});
      dataOut({'name': "category", 'value': cybcon_was.showAttribute(WMID, 'category'), 'description': "Category", 'tagname': "category"});
      dataOut({'name': "workTimeout", 'value': cybcon_was.showAttribute(WMID, 'workTimeout'), 'unit': "milliseconds", 'description': "Work timeout", 'tagname': "worktimeout"});
      dataOut({'name': "workReqQSize", 'value': cybcon_was.showAttribute(WMID, 'workReqQSize'), 'unit': "work objects", 'description': "Work request queue size", 'tagname': "workreqqsize"});
      dataOut({'name': "workReqQFullAction", 'value': cybcon_was.showAttribute(WMID, 'workReqQFullAction'), 'description': "Work request queue full action", 'tagname': "workreqqfullaction"});
      dataOut({'description': "Service names", 'tagname': "servicenames", 'tagtype': "1"});
      if cybcon_was.showAttribute(WMID, 'serviceNames').lower().find("appprofileservice") != -1:
        dataOut({'name': "serviceName", 'value': "true", 'description': "Application Profiling Service (deprecated)", 'tagname': "servicename"});
      else:
        dataOut({'name': "serviceName", 'value': "false", 'description': "Application Profiling Service (deprecated)", 'tagname': "servicename"});
      if cybcon_was.showAttribute(WMID, 'serviceNames').lower().find("userworkarea") != -1:
        dataOut({'name': "serviceName", 'value': "true", 'description': "WorkArea", 'tagname': "servicename"});
      else:
        dataOut({'name': "serviceName", 'value': "false", 'description': "WorkArea", 'tagname': "servicename"});
      if cybcon_was.showAttribute(WMID, 'serviceNames').lower().find("security") != -1:
        dataOut({'name': "serviceName", 'value': "true", 'description': "Security", 'tagname': "servicename"});
      else:
        dataOut({'name': "serviceName", 'value': "false", 'description': "Security", 'tagname': "servicename"});
      if cybcon_was.showAttribute(WMID, 'serviceNames').lower().find("com.ibm.ws.i18n") != -1:
        dataOut({'name': "serviceName", 'value': "true", 'description': "Internationalization", 'tagname': "servicename"});
      else:
        dataOut({'name': "serviceName", 'value': "false", 'description': "Internationalization", 'tagname': "servicename"});
      dataOut({'tagname': "servicenames", 'tagtype': "2"});

      dataOut({'description': "Thread pool properties", 'tagname': "threadpoolproperties", 'tagtype': "1"});
      dataOut({'name': "numAlarmThreads", 'value': cybcon_was.showAttribute(WMID, 'numAlarmThreads'), 'unit': "threads", 'description': "Number of alarm threads", 'tagname': "numalarmthreads"});
      dataOut({'name': "minThreads", 'value': cybcon_was.showAttribute(WMID, 'minThreads'), 'unit': "threads", 'description': "Minimum number of threads", 'tagname': "minthreads"});
      dataOut({'name': "maxThreads", 'value': cybcon_was.showAttribute(WMID, 'maxThreads'), 'unit': "threads", 'description': "Maximum number of threads", 'tagname': "maxthreads"});
      dataOut({'name': "threadPriority", 'value': cybcon_was.showAttribute(WMID, 'threadPriority'), 'unit': "priority", 'description': "Thread Priority", 'tagname': "threadpriority"});
      dataOut({'name': "isGrowable", 'value': cybcon_was.showAttribute(WMID, 'isGrowable'), 'description': "Growable", 'tagname': "isgrowable"});
      dataOut({'tagname': "threadpoolproperties", 'tagtype': "2"});

      dataOut({'description': "Custom properties", 'tagname': "customproperties", 'tagtype': "1"});
      CusProp="";
      for CusProp in cybcon_was.splitArray(cybcon_was.showAttribute(WMID, 'customProperties')):
        dataOut({'name': "customProperty", 'value': cybcon_was.showAttribute(CusProp, 'value'), 'description': cybcon_was.showAttribute(CusProp, 'name'), 'tagname': "property"});
      if CusProp == "":
        dataOut({'value': "No custom properties set."});
      dataOut({'tagname': "customproperties", 'tagtype': "2"});

      dataOut({'tagname': "workmanager", 'tagtype': "2"});
    else:
      dataOut({'value': "No work managers configured on this scope."});
  dataOut({'tagname': "workmanagers", 'tagtype': "2"});
  dataOut({'tagname': "asyncbeans", 'tagtype': "2"});

#----------------------------------------------------------------------------
# get_CacheInstances
#   description: search the cache instances properties by it's given objectID
#   input: objectID (can be cellID, clusterID, nodeID or serverID)
#   output: informations on stdout
#   return: -
#----------------------------------------------------------------------------
def get_CacheInstances(objectID):
  dataOut({'description': "Cache instances", 'tagname': "cacheinstances", 'tagtype': "1"});
  dataOut({'description': "Object cache instances", 'tagname': "objectcacheinstances", 'tagtype': "1"});

  for cacheInstanceID in AdminConfig.list('ObjectCacheInstance', objectID).split(lineSeparator):
    if cacheInstanceID != "":
      dataOut({'tagname': "cacheinstance", 'tagtype': "1"});
      dataOut({'name': "name", 'value': cybcon_was.showAttribute(cacheInstanceID, 'name'), 'description': "Name", 'tagname': "name"});
      dataOut({'name': "jndiName", 'value': cybcon_was.showAttribute(cacheInstanceID, 'jndiName'), 'description': "JNDI name", 'tagname': "jndiName"});
      dataOut({'name': "description", 'value': cybcon_was.showAttribute(cacheInstanceID, 'description'), 'description': "Description", 'tagname': "description"});
      dataOut({'name': "cacheSize", 'value': cybcon_was.showAttribute(cacheInstanceID, 'cacheSize'), 'unit': "entries", 'description': "Cache size", 'tagname': "cacheSize"});
      dataOut({'name': "defaultPriority", 'value': cybcon_was.showAttribute(cacheInstanceID, 'defaultPriority'), 'description': "Default priority", 'tagname': "defaultPriority"});

      dataOut({'description': "Disk cache settings", 'tagname': "diskcachesettings", 'tagtype': "1"});
      dataOut({'name': "enableDiskOffload", 'value': cybcon_was.showAttribute(cacheInstanceID, 'enableDiskOffload'), 'description': "Enable disk offload", 'tagname': "enableDiskOffload"});
      dataOut({'tagname': "diskcachesettings", 'tagtype': "2"});

      dataOut({'description': "Consistency settings", 'tagname': "consistencysettings", 'tagtype': "1"});
      dataOut({'name': "useListenerContext", 'value': cybcon_was.showAttribute(cacheInstanceID, 'useListenerContext'), 'description': "Use listener context", 'tagname': "useListenerContext"});
      if cybcon_was.showAttribute(cacheInstanceID, 'disableDependencyId') == "false":
        dataOut({'name': "disableDependencyId", 'value': "true", 'description': "Dependency ID support", 'tagname': "disableDependencyId"});
      else:
        dataOut({'name': "disableDependencyId", 'value': "false", 'description': "Dependency ID support", 'tagname': "disableDependencyId"});
      dataOut({'name': "enableCacheReplication", 'value': cybcon_was.showAttribute(cacheInstanceID, 'enableCacheReplication'), 'description': "Enable cache replication", 'tagname': "enableCacheReplication"});
      dataOut({'tagname': "consistencysettings", 'tagtype': "2"});
      dataOut({'tagname': "cacheinstance", 'tagtype': "2"});
    else:
      dataOut({'value': "No cache instance defined on this scope."});
  dataOut({'tagname': "objectcacheinstances", 'tagtype': "2"});
  dataOut({'tagname': "cacheinstances", 'tagtype': "2"});


#----------------------------------------------------------------------------
# get_clusterMembers
#   description: output cluster members of given clusterID
#   input: clusterID
#   output: informations on stdout
#   return: -
#----------------------------------------------------------------------------
def get_clusterMembers(clusterID):
  dataOut({'description': "Cluster members", 'tagname': "clustermembers", 'tagtype': "1"});
  clusterMember="";
  for clusterMember in cybcon_was.splitArray(cybcon_was.showAttribute(clusterID, 'members')):
    if clusterMember != "":
      dataOut({'tagname': "clustermember", 'tagtype': "1"});
      dataOut({'name': "memberName", 'value': cybcon_was.showAttribute(clusterMember, 'memberName'), 'description': "Member name", 'tagname': "memberName"});
      dataOut({'name': "weight", 'value': cybcon_was.showAttribute(clusterMember, 'weight'), 'description': "Configured weight", 'tagname': "weight"});
      dataOut({'tagname': "clustermember", 'tagtype': "2"});
  if clusterMember == "":
    dataOut({'value': "No cluster member found in this cluster."});
  dataOut({'tagname': "clustermembers", 'tagtype': "2"});

#----------------------------------------------------------------------------
# get_enterpriseApplicationStartupBehavior
#   description: output information about the applications startup behavior
#   input: id deplObjectID
#   output: informations on stdout
#   return: -
#----------------------------------------------------------------------------
def get_enterpriseApplicationStartupBehavior(deplObjectID):
  dataOut({'tagname': 'startupBehavior', 'description': "Startup behavior", 'tagtype': "1"});
  dataOut({'name': 'startingWeight', 'value': cybcon_was.showAttribute(deplObjectID, 'startingWeight'), 'description': 'Startup order', 'tagname': 'startingWeight'});
  dataOut({'name': 'backgroundApplication', 'value': cybcon_was.showAttribute(deplObjectID, 'backgroundApplication'), 'description': 'Launch application before server completes startup', 'tagname': 'backgroundApplication'});
  dataOut({'name': 'createMBeansForResources', 'value': cybcon_was.showAttribute(deplObjectID, 'createMBeansForResources'), 'description': 'Create MBeans for resources', 'tagname': 'createMBeansForResources'});
  dataOut({'tagname': 'startupBehavior', 'tagtype': "2"});

#----------------------------------------------------------------------------
# get_enterpriseApplicationBinaries
#   description: output information about the applications binaries
#   input: string appName, id deplObjectID
#   output: informations on stdout
#   return: -
#----------------------------------------------------------------------------
def get_enterpriseApplicationBinaries(appName, deplObjectID):
  dataOut({'tagname': "appbinaries", 'description': "Application binaries", 'tagtype': "1"});

  # read some applications data from AdminApp.view
  # set default value
  appLocation = "";
  appBuildID = "";
  for appConfig in AdminApp.view(appName).split(lineSeparator):
    if appConfig.find("Application Build ID") != -1:
      appBuildID = appConfig.replace("Application Build ID", "").replace(":", "").strip();
      continue;
    if appConfig.find("Directory to install application") != -1:
      appLocation = appConfig.replace("Directory to install application", "").replace(":", "").strip();
      continue;

  # output data
  dataOut({'name': "installedeardestination", 'value': appLocation, 'description': "Location (full path)", 'tagname': "installedeardestination"});
  dataOut({'name': "binariesURL", 'value': cybcon_was.showAttribute(deplObjectID, 'binariesURL'), 'description': "Location (binariesURL)", 'tagname': "binariesURL"});
  dataOut({'name': "useMetadataFromBinaries", 'value': cybcon_was.showAttribute(deplObjectID, 'useMetadataFromBinaries'), 'description': "Use configuration information in binary", 'tagname': "useMetadataFromBinaries"});
  dataOut({'name': "enableDistribution", 'value': cybcon_was.showAttribute(deplObjectID, 'enableDistribution'), 'description': "Enable binary distribution, expansion and cleanup post uninstallation", 'tagname': "enableDistribution"});
  dataOut({'name': "filepermission", 'value': cybcon_was.showAttribute(deplObjectID, 'filePermission'), 'description': "File permissions", 'tagname': "filepermission"});
  dataOut({'name': "buildversion", 'value': appBuildID, 'description': "Application build level", 'tagname': "buildversion"});
  dataOut({'tagname': "appbinaries", 'tagtype': "2"});

#----------------------------------------------------------------------------
# get_enterpriseApplicationClassloading
#   description: output information about the applications classloaders
#   input: id deplObjectID
#   output: informations on stdout
#   return: -
#----------------------------------------------------------------------------
def get_enterpriseApplicationClassloading(deplObjectID):

  dataOut({'tagname': "appclassloaders", 'description': "Class loading and update detection", 'tagtype': "1"});

  dataOut({'name': "reloadEnabled", 'value': cybcon_was.showAttribute(deplObjectID, 'reloadEnabled'), 'description': "Reload classes when application files are updated", 'tagname': "reloadEnabled"});
  dataOut({'name': "reloadInterval", 'value': cybcon_was.showAttribute(deplObjectID, 'reloadInterval'), 'unit': "seconds", 'description': "Polling interval for updated files", 'tagname': "reloadInterval"});

  dataOut({'tagname': "classloader", 'tagtype': "1"});
  classLoaderID = cybcon_was.showAttribute(deplObjectID, 'classloader');
  if classLoaderID != -1:
    dataOut({'name': "mode", 'value': cybcon_was.showAttribute(classLoaderID, 'mode'), 'description': "Class loader order", 'tagname': "mode"});
  else:
    dataOut({'value': "No classloader defined."});
  dataOut({'tagname': "classloader", 'tagtype': "2"});

  dataOut({'tagname': "warclassloader", 'tagtype': "1"});
  dataOut({'name': "warClassLoaderPolicy", 'value': cybcon_was.showAttribute(deplObjectID, 'warClassLoaderPolicy'), 'description': "WAR class loader policy", 'tagname': "warClassLoaderPolicy"});
  dataOut({'tagname': "warclassloader", 'tagtype': "2"});
  
  dataOut({'tagname': "appclassloaders", 'tagtype': "2"});

#----------------------------------------------------------------------------
# get_enterpriseApplicationRequestDispatcher
#   description: output information about the applications request dispatcher
#   input: id deplObjectID
#   output: informations on stdout
#   return: -
#----------------------------------------------------------------------------
def get_enterpriseApplicationRequestDispatcher(deplObjectID):
  dataOut({'tagname': 'requestDispatcher', 'description': 'Request dispatcher properties', 'tagtype': '1'});
  dataOut({'name': 'allowDispatchRemoteInclude', 'value': cybcon_was.showAttribute(deplObjectID, 'allowDispatchRemoteInclude'), 'description': 'Allow dispatching includes to remote resources', 'tagname': 'allowDispatchRemoteInclude'});
  dataOut({'name': 'allowServiceRemoteInclude', 'value': cybcon_was.showAttribute(deplObjectID, 'allowServiceRemoteInclude'), 'description': 'Allow servicing includes from remote resources', 'tagname': 'allowServiceRemoteInclude'});
  dataOut({'name': 'asyncRequestDispatchType', 'value': cybcon_was.showAttribute(deplObjectID, 'asyncRequestDispatchType'), 'description': 'Asynchronous request dispatching type', 'tagname': 'asyncRequestDispatchType'});
  dataOut({'tagname': 'requestDispatcher', 'tagtype': '2'});

#----------------------------------------------------------------------------
# get_enterpriseApplicationLibraryReferences
#   description: output information about the applications shared libs
#   input: id deplObjectID
#   output: informations on stdout
#   return: -
#----------------------------------------------------------------------------
def get_enterpriseApplicationLibraryReferences(deplObjectID):

  dataOut({'tagname': "sharedlibref", 'description': "Shared library references", 'tagtype': "1"});

  dataOut({'tagname': "appsharedlibref", 'description': "Application", 'tagtype': "1"});
  classLoaderID = cybcon_was.showAttribute(deplObjectID, 'classloader');
  if classLoaderID != -1:
    appSharedLibraryID = "";
    for appSharedLibraryID in cybcon_was.splitArray(cybcon_was.showAttribute(classLoaderID, 'libraries')):
      dataOut({'name': "libraryName", 'value': cybcon_was.showAttribute(appSharedLibraryID, 'libraryName'), 'description': "Library Name", 'tagname': "libraryName"});
    if appSharedLibraryID == "":
      dataOut({'value': "No Shared Library References defined."});
  else:
    dataOut({'value': "No Shared Library References defined."});
  dataOut({'tagname': "appsharedlibref", 'tagtype': "2"});

  dataOut({'tagname': "webmodules", 'description': "Module(s)", 'tagtype': "1"});
  webModExist = "false";
  for webModuleID in cybcon_was.splitArray(cybcon_was.showAttribute(deplObjectID, 'modules')):
    uri = cybcon_was.showAttribute(webModuleID, 'uri');
    # check for webarchive - skip jar files
    if uri.find(".war") != -1:
      webModExist = "true";
      dataOut({'tagname': "webmodule", 'tagtype': "1"});
      dataOut({'name': "uri", 'value': uri + ",WEB-INF/web.xml", 'description': "URI", 'tagname': "uri"});
      dataOut({'tagname': "webmodsharedlibref", 'tagtype': "1"});
      classLoaderID = cybcon_was.showAttribute(webModuleID, 'classloader');
      if classLoaderID != -1:
        modSharedLibraryID = "";
        for modSharedLibraryID in cybcon_was.splitArray(cybcon_was.showAttribute(classLoaderID, 'libraries')):
          dataOut({'name': "libraryName", 'value': cybcon_was.showAttribute(modSharedLibraryID, 'libraryName'), 'description': "Library Name", 'tagname': "libraryName"});
        if modSharedLibraryID == "":
          dataOut({'value': "No Shared Library References defined."});
      else:
        dataOut({'value': "No Shared Library References defined."});
      dataOut({'tagname': "webmodsharedlibref", 'tagtype': "2"});
      dataOut({'tagname': "webmodule", 'tagtype': "2"});
  if webModExist == "false":
    dataOut({'value': "No web module in enterprise application."});
  dataOut({'tagname': "webmodules", 'tagtype': "2"});
    
  dataOut({'tagname': "sharedlibref", 'tagtype': "2"});

#----------------------------------------------------------------------------
# get_enterpriseApplicationSessionManagement
#   description: output information about the applications session management
#   input: id deplObjectID
#   output: informations on stdout
#   return: -
#----------------------------------------------------------------------------
def get_enterpriseApplicationSessionManagement(deplObjectID):
  dataOut({'tagname': 'sessionManagement', 'description': 'Session management', 'tagtype': '1'});

  deplObjectConfigID=cybcon_was.splitArray(cybcon_was.showAttribute(deplObjectID, 'configs'));
  if len(deplObjectConfigID) == 0:
    deplObjectConfigID = "";
  else:
    deplObjectConfigID=deplObjectConfigID[0];
  
  if deplObjectConfigID != "":
    sessionManagementID=cybcon_was.showAttribute(deplObjectConfigID, 'sessionManagement');
    if sessionManagementID != "":
      dataOut({'name': 'enable', 'value': cybcon_was.showAttribute(sessionManagementID, 'enable'), 'description': "Override session management", 'tagname': 'enable'});
      dataOut({'name': 'enableSSLTracking', 'value': cybcon_was.showAttribute(sessionManagementID, 'enableSSLTracking'), 'description': 'Enable SSL ID tracking', 'tagname': 'enableSSLTracking'});
      dataOut({'name': 'enableCookies', 'value': cybcon_was.showAttribute(sessionManagementID, 'enableCookies'), 'description': 'Enable cookies', 'tagname': 'enableCookies'});
      defaultCookieSettingsID = cybcon_was.showAttribute(sessionManagementID, 'defaultCookieSettings');
      if defaultCookieSettingsID != "":
        dataOut({'tagname': 'defaultCookieSettings', 'description': 'cookie', 'tagtype': '1'});
        dataOut({'name': 'name', 'value': cybcon_was.showAttribute(defaultCookieSettingsID, 'name'), 'description': 'Cookie name', 'tagname': 'name'});
        dataOut({'name': 'secure', 'value': cybcon_was.showAttribute(defaultCookieSettingsID, 'secure'), 'description': 'Restrict cookies to HTTPS sessions', 'tagname': 'secure'});
        dataOut({'name': 'httpOnly', 'value': cybcon_was.showAttribute(defaultCookieSettingsID, 'httpOnly'), 'description': 'Set session cookies to HTTPOnly to help prevent cross-site scripting attacks', 'tagname': 'httpOnly'});
        dataOut({'name': 'domain', 'value': cybcon_was.showAttribute(defaultCookieSettingsID, 'domain'), 'description': 'Cookie domain', 'tagname': 'domain'});
        maximumAge=cybcon_was.showAttribute(defaultCookieSettingsID, 'maximumAge');
        if maximumAge == "-1":
          dataOut({'name': 'cookieMaximumAge', 'value': 'Current browser session', 'description': 'cookieMaximumAge', 'tagname': 'cookieMaximumAge'});
        else:
          dataOut({'name': 'cookieMaximumAge', 'value': maximumAge, 'unit': 'seconds', 'description': 'cookieMaximumAge', 'tagname': 'cookieMaximumAge'});
        
        dataOut({'name': 'useContextRootAsPath', 'value': cybcon_was.showAttribute(defaultCookieSettingsID, 'useContextRootAsPath'), 'description': 'Use the context root', 'tagname': 'useContextRootAsPath'});
        dataOut({'name': 'path', 'value': cybcon_was.showAttribute(defaultCookieSettingsID, 'path'), 'description': 'Set cookie path', 'tagname': 'path'});
        dataOut({'tagname': 'defaultCookieSettings', 'tagtype': '2'});

      dataOut({'name': 'enableUrlRewriting', 'value': cybcon_was.showAttribute(sessionManagementID, 'enableUrlRewriting'), 'description': 'Enable URL rewriting', 'tagname': 'enableUrlRewriting'});
      dataOut({'name': 'enableProtocolSwitchRewriting', 'value': cybcon_was.showAttribute(sessionManagementID, 'enableProtocolSwitchRewriting'), 'description': 'Enable protocol switch rewriting', 'tagname': 'enableProtocolSwitchRewriting'});

      tuningParamsID = cybcon_was.showAttribute(sessionManagementID, 'tuningParams');
      if tuningParamsID != "":
        dataOut({'name': 'maxInMemorySessionCount', 'value': cybcon_was.showAttribute(tuningParamsID, 'maxInMemorySessionCount'), 'unit': 'sessions', 'description': 'Maximum in-memory session count', 'tagname': 'maxInMemorySessionCount'});
        dataOut({'name': 'allowOverflow', 'value': cybcon_was.showAttribute(tuningParamsID, 'allowOverflow'), 'description': 'Allow overflow', 'tagname': 'allowOverflow'});
        dataOut({'name': 'invalidationTimeout', 'value': cybcon_was.showAttribute(tuningParamsID, 'invalidationTimeout'), 'unit': 'minutes', 'description': 'Session timeout', 'tagname': 'invalidationTimeout'});

      dataOut({'name': 'enableSecurityIntegration', 'value': cybcon_was.showAttribute(sessionManagementID, 'enableSecurityIntegration'), 'description': 'Security integration', 'tagname': 'enableSecurityIntegration'});
      dataOut({'name': 'allowSerializedSessionAccess', 'value': cybcon_was.showAttribute(sessionManagementID, 'allowSerializedSessionAccess'), 'description': 'Allow serial access', 'tagname': 'allowSerializedSessionAccess'});
      dataOut({'name': 'maxWaitTime', 'value': cybcon_was.showAttribute(sessionManagementID, 'maxWaitTime'), 'unit': 'seconds', 'description': 'Maximum wait time', 'tagname': 'maxWaitTime'});
      dataOut({'name': 'accessSessionOnTimeout', 'value': cybcon_was.showAttribute(sessionManagementID, 'accessSessionOnTimeout'), 'description': 'Allow access on timeout', 'tagname': 'accessSessionOnTimeout'});
      
    else:
      dataOut({'name': 'Overridesessionmanagement', 'value': 'false', 'description': "Override session management", 'tagname': 'Overridesessionmanagement'});
  else:
    dataOut({'name': 'Overridesessionmanagement', 'value': 'false', 'description': "Override session management", 'tagname': 'Overridesessionmanagement'});
    
  dataOut({'tagname': 'sessionManagement', 'tagtype': '2'});

#----------------------------------------------------------------------------
# get_enterpriseApplicationJSPandJSFoptions
#   description: output information about the applications JSF and JSP options
#   input: string applicationName, id deplObjectID
#   output: informations on stdout
#   return: -
#----------------------------------------------------------------------------
def get_enterpriseApplicationJSPandJSFoptions(appName, deplObjectID):
  dataOut({'tagname': 'jSPAndJSFoptions', 'description': 'JSP and JSF options', 'tagtype': '1'});

  # parse webmodule informations from AdminApp.view()
  webModules=[];
  innerWebModule='false';
  webModule={};
  webModule['module']="";
  webModule['URI']="";
  webModule['reload']="";
  webModule['interval']="";
  wm_name="";
  wm_name_last="";
  try:
    for appConfig in AdminApp.view(appName, '[ -JSPReloadForWebMod ]').split(lineSeparator):
      if appConfig.find("Web module:") != -1:
        wm_name = appConfig.replace("Web module:", "").strip();
        if wm_name != wm_name_last:
          if webModule['module'] != "":
            webModules.append(webModule);
            webModule={};
            webModule['module']="";
            webModule['URI']="";
            webModule['reload']="";
            webModule['interval']="";
          webModule['module'] = wm_name;
          wm_name_last = wm_name;
        continue;
      elif appConfig.find("URI:") != -1:
        uri = appConfig.replace("URI:", "").strip();
        if wm_name != "":
          webModule['URI'] = uri;
        continue;
      elif appConfig.find("JSP enable class reloading:") != -1:
        reload = appConfig.replace("JSP enable class reloading:", "").strip();
        if wm_name != "":
          webModule['reload'] = reload;
        continue;
      elif appConfig.find("JSP reload interval in seconds:") != -1:
        interval = appConfig.replace("JSP reload interval in seconds:", "").strip();
        if wm_name != "":
          webModule['interval'] = interval;
        continue;
    if webModule['module'] != "": webModules.append(webModule);

    # loop over webmodules
    dataOut({'tagname': 'webmodules', 'description': 'JSP reloading options for Web modules', 'tagtype': '1'});
    for webModule in webModules:
      dataOut({'tagname': 'webmodule', 'tagtype': '1'});
      dataOut({'name': 'webmodule', 'value': webModule['module'], 'description': "Web module", 'tagname': 'webmodule'});
      dataOut({'name': 'URI', 'value': webModule['URI'], 'description': "URI", 'tagname': 'URI'});
      dataOut({'name': 'jspenableclassreloading', 'value': webModule['reload'], 'description': "JSP enable class reloading", 'tagname': 'jspenableclassreloading'});
      dataOut({'name': 'jspreloadintervalinseconds', 'value': webModule['interval'], 'unit': 'seconds', 'description': 'JSP reload interval in seconds', 'tagname': 'jspreloadintervalinseconds'});
      dataOut({'tagname': 'webmodule', 'tagtype': '2'});
    dataOut({'tagname': 'webmodules', 'tagtype': '2'});
  except:
    dataOut({'description': 'WARNING', 'value': 'The Server not supports taskname JSPReloadForWebMod in AdminApp.view', 'tagname': 'WARNING'});

  try:
    JSFimplementation = AdminTask.listJSFImplementation(appName);
    dataOut({'name': 'JSFimplementation', 'value': JSFimplementation, 'description': "Select a JSF implementation that the container will use for this application", 'tagname': 'JSFimplementation'});
  except:
    dataOut({'description': 'WARNING', 'value': 'The Server not supports AdminTask.listJSFImplementation().', 'tagname': 'WARNING'});

  dataOut({'tagname': 'jSPAndJSFoptions', 'tagtype': '2'});


#----------------------------------------------------------------------------
# get_enterpriseApplicationTargetAndState
#   description: output targetMappings and RunState
#   input: string appName, flag targetMapping, flag runState
#   output: informations on stdout
#   return: -
#----------------------------------------------------------------------------
def get_enterpriseApplicationTargetAndState(appName, targetMapping, runState):
  if targetMapping == "true":
    for serverName in cybcon_was.get_applicationTargetServerNames(appName):
      if runState == "true":
        dataOut({'name': "servername", 'value': serverName, 'description': "Application target server", 'tagname': "servername", 'tagtype': "1"});
        dataOut({'name': "applicationstatus", 'value': cybcon_was.get_applicationStateOnServer(appName, serverName), 'description': "Application Status", 'tagname': "applicationstatus"});
        dataOut({'tagname': "servername", 'tagtype': "2"});
      else:
        dataOut({'name': "servername", 'value': serverName, 'description': "Application target server", 'tagname': "servername"});
  else:
    dataOut({'name': "applicationstatus", 'value': cybcon_was.get_applicationState(appName), 'description': "Application Status", 'tagname': "applicationstatus"});

#----------------------------------------------------------------------------
# get_CORBANamingService
#   description: output information about CORBA Naming Service Users and
#     Groups
#   input: cell ID
#   output: informations on stdout
#   return: -
#----------------------------------------------------------------------------
def get_CORBANamingService(cellID):
  # definig hash table for the  CORBA Naming Service Groups informations
  groups={};
  # definig hash table for the  CORBA Naming Service Users informations
  users={};

  for authTableExtID in AdminConfig.list('AuthorizationTableExt', cellID).split(lineSeparator):
    if cybcon_was.showAttribute(authTableExtID, 'fileName') == "naming-authz.xml":
      for authID in cybcon_was.splitArray(cybcon_was.showAttribute(authTableExtID, 'authorizations')):
        # get the Role Names, only the 4 roles are valid
        roleName = cybcon_was.showAttribute(cybcon_was.showAttribute(authID, 'role'), 'roleName');
        if roleName == "CosNamingCreate":   roleName = "Cos Naming Create";
        elif roleName == "CosNamingDelete": roleName = "Cos Naming Delete";
        elif roleName == "CosNamingRead":   roleName = "Cos Naming Read";
        elif roleName == "CosNamingWrite":  roleName = "Cos Naming Write";
        else: continue;
  
        # get Group Names which have that role
        auth_grps=[];
        for groupID in cybcon_was.splitArray(cybcon_was.showAttribute(authID, 'groups')):
          if groupID != "":
            groupName = cybcon_was.showAttribute(groupID, 'name');
            if auth_grps.count(groupName) == 0: auth_grps.append(groupName);
        # get User Names which have that role
        auth_usrs=[];
        for userID in cybcon_was.splitArray(cybcon_was.showAttribute(authID, 'users')):
          if userID != "":
            userName = cybcon_was.showAttribute(userID, 'name');
            if auth_users.count(userName) == 0: auth_usrs.append(userName);
        # get Special Subject Names whih have that role
        for spSubjectID in cybcon_was.splitArray(cybcon_was.showAttribute(authID, 'specialSubjects')):
          if spSubjectID != "":
            [ foo, subjectName ] = spSubjectID.split("#");
            [ subjectName, foo ] = subjectName.split("_");
            if subjectName == "EveryoneExt": subjectName="EVERYONE";
            if subjectName == "AllAuthenticatedUsersExt": subjectName="ALL_AUTHENTICATED";
            if subjectName == "ServerExt": continue;
            if auth_grps.count(subjectName) == 0: auth_grps.append(subjectName);

        # loop over temporary user and group array and append role to the hashtable
        for auth_grp in auth_grps:
          if auth_grp != "":
            if groups.has_key(auth_grp) != 1: groups[auth_grp]=[];
            if groups[auth_grp].count(roleName) == 0: groups[auth_grp].append(roleName);
        for auth_usr in auth_usrs:
          if auth_usr != "":
            if users.has_key(auth_usr) != 1: users[auth_usr]=[];
            if users[auth_usr].count(roleName) == 0: users[auth_usr].append(roleName);

  # Output CORBA Naming Service Users
  dataOut({'tagname': "corbanamingserviceusers", 'description': "CORBA Naming Service Users", 'tagtype': "1"});
  usr="";
  for usr in users.keys():
    if usr != "":
      dataOut({'tagname': "corbanamingserviceuser", 'tagtype': "1"});
      dataOut({'value': usr, 'description': "User", 'tagname': "user"});
      dataOut({'description': "Role(s)", 'tagname': "roles", 'tagtype': "1"});
      for role in users[usr]:
        dataOut({'value': role, 'tagname': "role"});
      dataOut({'tagname': "roles", 'tagtype': "2"});
      dataOut({'tagname': "corbanamingserviceuser", 'tagtype': "2"});
  if usr == "":
    dataOut({'value': "No CORBA Naming Service Users defined."});
  dataOut({'tagname': "corbanamingserviceusers", 'tagtype': "2"});

  # Output CORBA Naming Service Groups
  dataOut({'tagname': "corbanamingservicegroups", 'description': "CORBA Naming Service Groups", 'tagtype': "1"});
  grp = "";
  for grp in groups.keys():
    if grp != "":
      dataOut({'tagname': "corbanamingservicegroup", 'tagtype': "1"}); 
      dataOut({'value': grp, 'description': "Group", 'tagname': "group"}); 
      dataOut({'description': "Role(s)", 'tagname': "roles", 'tagtype': "1"}); 
      for role in groups[grp]:
        dataOut({'value': role, 'tagname': "role"}); 
      dataOut({'tagname': "roles", 'tagtype': "2"}); 
      dataOut({'tagname': "corbanamingservicegroup", 'tagtype': "2"});
  if grp == "":
    dataOut({'value': "No CORBA Naming Service Groups defined."});
  dataOut({'tagname': "corbanamingservicegroups", 'tagtype': "2"});

#----------------------------------------------------------------------------
# get_webServerProperties
#   description: get general properties from webservers
#   input: serverEntry, serverID
#   output: informations on stdout
#   return: -
#----------------------------------------------------------------------------
def get_webServerProperties(serverEntry, serverID):
  dataOut({'description': "General Properties", 'tagname': "generalproperties", 'tagtype': "1"});
  dataOut({'name': "servername", 'value': cybcon_was.showAttribute(serverEntry, 'serverName'), 'description': "Web server name", 'tagname': "servername"});

  componentID=cybcon_was.splitArray(cybcon_was.showAttribute(serverID, 'components'))[0];
  if componentID != "":
    dataOut({'name': "webserverType", 'value': cybcon_was.showAttribute(componentID, 'webserverType'), 'description': "Type", 'tagname': "webserverType"});

  for endpointPort in cybcon_was.splitArray(cybcon_was.showAttribute(serverEntry, 'specialEndpoints')):
    if cybcon_was.showAttribute(endpointPort, 'endPointName') == "WEBSERVER_ADDRESS":
      dataOut({'name': "Port", 'value': cybcon_was.showAttribute(cybcon_was.showAttribute(endpointPort, 'endPoint'), 'port'), 'description': "Port", 'tagname': "Port"});

  if componentID != "":
    dataOut({'name': "webserverInstallRoot", 'value': cybcon_was.showAttribute(componentID, 'webserverInstallRoot'), 'description': "Web server installation location", 'tagname': "webserverInstallRoot"});
    dataOut({'name': "configurationFilename", 'value': cybcon_was.showAttribute(componentID, 'configurationFilename'), 'description': "Configuration file name", 'tagname': "configurationFilename"});

  dataOut({'tagname': "generalproperties", 'tagtype': "2"});


#----------------------------------------------------------------------------
# get_webServerLogging
#   description: get logging properties
#   input: serverID
#   output: informations on stdout
#   return: -
#----------------------------------------------------------------------------
def get_webServerLogging(serverID):
  dataOut({'description': "Log file", 'tagname': "logfile", 'tagtype': "1"});

  componentID=cybcon_was.splitArray(cybcon_was.showAttribute(serverID, 'components'))[0];
  if componentID != "":
    dataOut({'name': "logFilenameAccess", 'value': cybcon_was.showAttribute(componentID, 'logFilenameAccess'), 'description': "Access log file name", 'tagname': "logFilenameAccess"});
    dataOut({'name': "logFilenameError", 'value': cybcon_was.showAttribute(componentID, 'logFilenameError'), 'description': "Error log file name", 'tagname': "logFilenameError"});

  dataOut({'description': "Log file", 'tagname': "logfile", 'tagtype': "2"});

#----------------------------------------------------------------------------
# get_webServerRemoteMgmnt
#   description: get informations about Remote Web server management
#   input: serverEntry, serverID
#   output: informations on stdout
#   return: -
#----------------------------------------------------------------------------
def get_webServerRemoteMgmnt(serverEntry, serverID):
  dataOut({'description': "Remote Web server management", 'tagname': "remotewebservermanagement", 'tagtype': "1"});

  for endpointPort in cybcon_was.splitArray(cybcon_was.showAttribute(serverEntry, 'specialEndpoints')):
    if cybcon_was.showAttribute(endpointPort, 'endPointName') == "WEBSERVER_ADMIN_ADDRESS":
      dataOut({'name': "Port", 'value': cybcon_was.showAttribute(cybcon_was.showAttribute(endpointPort, 'endPoint'), 'port'), 'description': "Port", 'tagname': "Port"});

  componentID=cybcon_was.splitArray(cybcon_was.showAttribute(serverID, 'components'))[0];
  if componentID != "":
    adminServerAuthID=cybcon_was.showAttribute(componentID, 'adminServerAuthentication');
    if adminServerAuthID != "":
      dataOut({'name': "userid", 'value': cybcon_was.showAttribute(adminServerAuthID, 'userid'), 'description': "Username", 'tagname': "userid"});
      dataOut({'name': "password", 'value': cybcon_was.showAttribute(adminServerAuthID, 'userid'), 'description': "Password", 'tagname': "password"});
    webserverAdminProtocol=cybcon_was.showAttribute(componentID, 'webserverAdminProtocol');
    if webserverAdminProtocol == "HTTP":
      dataOut({'name': "webserverAdminProtocol", 'value': "false", 'description': "Use SSL", 'tagname': "webserverAdminProtocol"});
    elif webserverAdminProtocol == "HTTPS":
      dataOut({'name': "webserverAdminProtocol", 'value': "true", 'description': "Use SSL", 'tagname': "webserverAdminProtocol"});
    else:
      dataOut({'name': "webserverAdminProtocol", 'value': webserverAdminProtocol, 'description': "Use SSL", 'tagname': "webserverAdminProtocol"});

  dataOut({'tagname': "remotewebservermanagement", 'tagtype': "2"});

#----------------------------------------------------------------------------
# get_webServerPlugin
#   description: get informations about Plug-in properties
#   input: serverID
#   output: informations on stdout
#   return: -
#----------------------------------------------------------------------------
def get_webServerPlugin(serverID):
  dataOut({'description': "Plug-in properties", 'tagname': "pluginproperties", 'tagtype': "1"});

  componentID=cybcon_was.splitArray(cybcon_was.showAttribute(serverID, 'components'))[0];
  if componentID != "":
    pluginPropID=cybcon_was.splitArray(cybcon_was.showAttribute(componentID, 'pluginProperties'))[0];
    if pluginPropID != "":
      dataOut({'name': "IgnoreDNSFailures", 'value': cybcon_was.showAttribute(pluginPropID, 'IgnoreDNSFailures'), 'description': "Ignore DNS failures during Web server startup", 'tagname': "IgnoreDNSFailures"});
      dataOut({'name': "RefreshInterval", 'value': cybcon_was.showAttribute(pluginPropID, 'RefreshInterval'), 'unit': "seconds", 'description': "Refresh configuration interval", 'tagname': "RefreshInterval"});

      dataOut({'description': "Repository copy of Web server plug-in files", 'tagname': "repositorycopy", 'tagtype': "1"});
      dataOut({'name': "ConfigFilename", 'value': cybcon_was.showAttribute(pluginPropID, 'ConfigFilename'), 'description': "Plug-in configuration file name", 'tagname': "ConfigFilename"});
      dataOut({'name': "PluginGeneration", 'value': cybcon_was.showAttribute(pluginPropID, 'PluginGeneration'), 'description': "Automatically generate the plug-in configuration file", 'tagname': "PluginGeneration"});
      dataOut({'name': "PluginPropagation", 'value': cybcon_was.showAttribute(pluginPropID, 'PluginPropagation'), 'description': "Automatically propagate plug-in configuration file", 'tagname': "PluginPropagation"});
      dataOut({'name': "KeyRingFilename", 'value': cybcon_was.showAttribute(pluginPropID, 'KeyRingFilename'), 'description': "Plug-in key store file name", 'tagname': "KeyRingFilename"});
      dataOut({'tagname': "repositorycopy", 'tagtype': "2"});

      dataOut({'description': "Web server copy of Web server plug-in files", 'tagname': "remotewebserverfiles", 'tagtype': "1"});
      dataOut({'name': "RemoteConfigFilename", 'value': cybcon_was.showAttribute(pluginPropID, 'RemoteConfigFilename'), 'description': "Plug-in configuration directory and file name", 'tagname': "RemoteConfigFilename"});
      dataOut({'name': "RemoteKeyRingFilename", 'value': cybcon_was.showAttribute(pluginPropID, 'RemoteKeyRingFilename'), 'description': "Plug-in key store directory and file name", 'tagname': "RemoteKeyRingFilename"});
      dataOut({'tagname': "remotewebserverfiles", 'tagtype': "2"});

      dataOut({'description': "Plug-in logging", 'tagname': "pluginlogging", 'tagtype': "1"});
      dataOut({'name': "LogFilename", 'value': cybcon_was.showAttribute(pluginPropID, 'LogFilename'), 'description': "Log file name", 'tagname': "LogFilename"});
      dataOut({'name': "LogLevel", 'value': cybcon_was.showAttribute(pluginPropID, 'LogLevel'), 'description': "Log level", 'tagname': "LogLevel"});
      dataOut({'tagname': "pluginlogging", 'tagtype': "2"});

      dataOut({'description': "Request and response", 'tagname': "requestandresponse", 'tagtype': "1"});
      dataOut({'name': "ResponseChunkSize", 'value': cybcon_was.showAttribute(pluginPropID, 'ResponseChunkSize'), 'unit': "KB", 'description': "Maximum chunk size used when reading the HTTP response body", 'tagname': "ResponseChunkSize"});
      ASDisableNagle=cybcon_was.showAttribute(pluginPropID, 'ASDisableNagle');
      if ASDisableNagle == "false":
        nagleenabled="true";
      elif ASDisableNagle == "true":
        nagleenabled="false";
      else:
        nagleenabled="unknown (" + ASDisableNagle + ")";
      dataOut({'name': "ASDisableNagle", 'value': nagleenabled, 'description': "Enable the Nagle Algorithm for connections to the Application Server", 'tagname': "ASDisableNagle"});
      dataOut({'name': "ChunkedResponse", 'value': cybcon_was.showAttribute(pluginPropID, 'ChunkedResponse'), 'description': "Chunk HTTP response to the client", 'tagname': "ChunkedResponse"});
      dataOut({'name': "AcceptAllContent", 'value': cybcon_was.showAttribute(pluginPropID, 'AcceptAllContent'), 'description': "Accept content for all requests", 'tagname': "AcceptAllContent"});
      VHostMatchingCompat=cybcon_was.showAttribute(pluginPropID, 'VHostMatchingCompat');
      if VHostMatchingCompat == "true":
        vhostmatch="Physically using the port specified in the request";
      elif VHostMatchingCompat == "false":
        vhostmatch="Logically using the port number from the host header";
      else:
        vhostmatch="unknown value (" + VHostMatchingCompat + ")";
      dataOut({'name': "VHostMatchingCompat", 'value': vhostmatch, 'description': "Virtual host matching", 'tagname': "VHostMatchingCompat"});
      dataOut({'name': "AppServerPortPreference", 'value': cybcon_was.showAttribute(pluginPropID, 'AppServerPortPreference'), 'description': "Application server port preference", 'tagname': "AppServerPortPreference"});
      dataOut({'tagname': "requestandresponse", 'tagtype': "2"});

      dataOut({'description': "Caching", 'tagname': "caching", 'tagtype': "1"});
      dataOut({'name': "ESIEnable", 'value': cybcon_was.showAttribute(pluginPropID, 'ESIEnable'), 'description': "Enable Edge Side Include (ESI) processing to cache the responses", 'tagname': "ESIEnable"});
      dataOut({'name': "ESIInvalidationMonitor", 'value': cybcon_was.showAttribute(pluginPropID, 'ESIInvalidationMonitor'), 'description': "Enable invalidation monitor to receive notifications", 'tagname': "ESIInvalidationMonitor"});
      dataOut({'name': "ESIMaxCacheSize", 'value': cybcon_was.showAttribute(pluginPropID, 'ESIMaxCacheSize'), 'unit': "KB", 'description': "Maximum cache size", 'tagname': "ESIMaxCacheSize"});
      dataOut({'tagname': "caching", 'tagtype': "2"});

      dataOut({'description': "Request routing", 'tagname': "requestrouting", 'tagtype': "1"});
      pluginRouteID=cybcon_was.showAttribute(pluginPropID, 'pluginServerClusterProperties');
      if pluginRouteID != "":
        dataOut({'name': "LoadBalance", 'value': cybcon_was.showAttribute(pluginRouteID, 'LoadBalance'), 'description': "Load balancing option", 'tagname': "LoadBalance"});
        dataOut({'name': "RetryInterval", 'value': cybcon_was.showAttribute(pluginRouteID, 'RetryInterval'), 'unit': "seconds", 'description': "Retry interval", 'tagname': "RetryInterval"});
        PostSizeLimit=cybcon_was.showAttribute(pluginRouteID, 'PostSizeLimit');
        if PostSizeLimit == "-1":
          dataOut({'name': "PostSizeLimit", 'value': "No Limit (" + PostSizeLimit + ")", 'description': "Maximum size of request content", 'tagname': "PostSizeLimit"});
        else:
          dataOut({'name': "PostSizeLimit", 'value': PostSizeLimit, 'unit':  "KBytes", 'description': "Maximum size of request content", 'tagname': "PostSizeLimit"});
        dataOut({'name': "PostBufferSize", 'value': cybcon_was.showAttribute(pluginRouteID, 'PostBufferSize'), 'unit':  "KBytes", 'description': "Maximum buffer size used when reading the HTTP request content", 'tagname': "PostBufferSize"});
        dataOut({'name': "RemoveSpecialHeaders", 'value': cybcon_was.showAttribute(pluginRouteID, 'RemoveSpecialHeaders'), 'description': "Remove special headers", 'tagname': "RemoveSpecialHeaders"});
        dataOut({'name': "CloneSeparatorChange", 'value': cybcon_was.showAttribute(pluginRouteID, 'CloneSeparatorChange'), 'description': "Clone separator change", 'tagname': "CloneSeparatorChange"});
      dataOut({'tagname': "requestrouting", 'tagtype': "2"});
  dataOut({'tagname': "pluginproperties", 'tagtype': "2"});

#############################################################################
# MAIN program
#############################################################################

#----------------------------------------------------------------------------
# PRE Operations
#----------------------------------------------------------------------------
# read in the configuration file
CONFIG = get_configuration(configFile);

#----------------------------------------------------------------------------
# cybcon_was
# export WebSphere libraries
sys.modules['AdminConfig'] = AdminConfig;
sys.modules['AdminControl'] = AdminControl;
sys.modules['AdminApp'] = AdminApp;
sys.modules['AdminTask'] = AdminTask;
sys.modules['Help'] = Help;
# set additional library path
sys.path.append(CONFIG['cybcon_was']['libPath']);
# import library
import cybcon_was;
# cybcon_was library copyright:
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so

# check required minimal version of cybcon_was:
CYBCON_WAS_VERSION=str(getattr(cybcon_was, "cybcon_was_lib_version"));
if CYBCON_WAS_VERSION < CONFIG['cybcon_was']['minVersion']:
  print "Minimum required cybcon_was library version is v" + CONFIG['cybcon_was']['minVersion'];
  print "but found version v" + CYBCON_WAS_VERSION;
  print "Please update the cybcon_was library from http://www.cybcon-industries.de/";
  print "Further processing skipped";
  sys.exit(1);
#----------------------------------------------------------------------------

#----------------------------------------------------------------------------
# MAIN Operations
#----------------------------------------------------------------------------
startTime = time.time();
if CONFIG['general']['output_format'] == "xml": print "<?xml version='1.0' encoding='iso-8859-1'?>";
dataOut({'tagname': "configcrawler", 'tagtype': "1"});
dataOut({'tagname': "head", 'tagtype': "1"});
dataOut({'tagname': "meta", 'name': "copyright", 'value': "Cybcon Industries 2009-" + time.strftime("%Y"), 'tagtype': "3"});
dataOut({'tagname': "meta", 'name': "product", 'value': "WebSphere configuration crawler", 'tagprops': [ "version='" + VERSION + "'", "library='cybcon_was v" + CYBCON_WAS_VERSION + "'" ], 'tagtype': "3"});
dataOut({'tagname': "meta", 'name': "author", 'value': "Michael Oberdorf", 'description': "Author", 'tagtype': "3"});
dataOut({'tagname': "meta", 'name': "date", 'value': time.strftime("%Y-%m-%d %H:%M:%S"), 'description': "Starting time at", 'tagtype': "3"});
dataOut({'tagname': "head", 'tagtype': "2"});
dataOut({'tagname': "configuration", 'tagtype': "1"});

#===========================================================================
# global configuration
if CONFIG['general']['services'] == "true":
  dataOut({'description': "Services", 'tagname': "services", 'tagtype': "1"});
  if CONFIG['services']['serviceProviders'] == "true": get_serviceProviders();
  if CONFIG['services']['policySets'] == "true": get_ApplicationPolicySets();
  dataOut({'tagname': "services", 'tagtype': "2"});

#===========================================================================
# get cell specific configuration
cellName = AdminControl.getCell();
cellID = AdminConfig.getid('/Cell:' + cellName + '/');

if CONFIG['general']['cell'] == "true":
  dataOut({'name': "Cell", 'value': cellName, 'description': "WAS cell", 'tagname': "cell", 'tagtype': "1"});
  # ----------------------------------------------
  # put in here cell specific configuration
  # ----------------------------------------------
  if CONFIG['cell']['CoreGroup'] == "true": get_CoreGroupProperties(cellID);
  dataOut({'description': "Resources (cell level)", 'tagname': "resources", 'tagtype': "1"});
  if CONFIG['cell']['JMS_provider'] == "true": get_JMSProviderProperties(cellID);
  if CONFIG['cell']['JDBC_provider'] == "true": get_JDBCProviderProperties(cellID);
  if CONFIG['cell']['ResourceAdapter'] == "true": get_ResourceAdapterProperties(cellID);
  if CONFIG['cell']['AsyncBeans'] == "true": get_AsyncBeans(cellID);
  if CONFIG['cell']['CacheInstances'] == "true": get_CacheInstances(cellID);
  if CONFIG['cell']['Mail_provider'] == "true": get_MailProviderProperties(cellID);
  if CONFIG['cell']['URL_provider'] == "true": get_URLProviderProperties(cellID);
  if CONFIG['cell']['ResourceEnv'] == "true": get_ResourceEnvironmentProperties(cellID);
  if CONFIG['cell']['Security'] == "true": get_securityProperties(cellName);
  dataOut({'tagname': "resources", 'tagtype': "2"});
  dataOut({'description': "Environment (cell level)", 'tagname': "environment", 'tagtype': "1"});
  if CONFIG['cell']['Virtual_hosts'] == "true": get_virtualHostProperties(cellID);
  if CONFIG['cell']['Websphere_variables'] == "true": get_variables(cellID);
  if CONFIG['cell']['Shared_libraries'] == "true": get_sharedLibraryProperties(cellID);
  if CONFIG['cell']['NameSpaceBindings'] == "true" or CONFIG['cell']['CORBANamingService'] == "true":
    dataOut({'description': "Naming", 'tagname': "naming", 'tagtype': "1"});
    if CONFIG['cell']['NameSpaceBindings'] == "true": get_nameSpaceBindingProperties(cellID);
    if CONFIG['cell']['CORBANamingService'] == "true": get_CORBANamingService(cellID);
    dataOut({'tagname': "naming", 'tagtype': "2"});
  if CONFIG['cell']['SIBus'] == "true": get_SIBusProperties(cellID);
  dataOut({'tagname': "environment", 'tagtype': "2"});

#===========================================================================
# loop over clusers
if CONFIG['general']['cluster'] == "true":
  dataOut({'tagname': "clusters", 'tagtype': "1"});
  for clusterName in cybcon_was.get_clusterNames():
    clusterID = AdminConfig.getid('/ServerCluster:' + clusterName + '/');
    dataOut({'name': "ServerCluster", 'value': clusterName, 'description': "WAS cluster", 'tagname': "cluster", 'tagtype': "1"});
    # ----------------------------------------------
    # put in here cluster specific configurations
    # ----------------------------------------------
    if CONFIG['cluster']['clusterMembers'] == "true": get_clusterMembers(clusterID);
    dataOut({'description': "Resources (cluster level)", 'tagname': "resources", 'tagtype': "1"});
    if CONFIG['cluster']['JMS_provider'] == "true": get_JMSProviderProperties(clusterID);
    if CONFIG['cluster']['JDBC_provider'] == "true": get_JDBCProviderProperties(clusterID);
    if CONFIG['cluster']['ResourceAdapter'] == "true": get_ResourceAdapterProperties(clusterID);
    if CONFIG['cluster']['AsyncBeans'] == "true": get_AsyncBeans(clusterID);
    if CONFIG['cluster']['CacheInstances'] == "true": get_CacheInstances(clusterID);
    if CONFIG['cluster']['Mail_provider'] == "true": get_MailProviderProperties(clusterID);
    if CONFIG['cluster']['URL_provider'] == "true": get_URLProviderProperties(clusterID);
    if CONFIG['cluster']['ResourceEnv'] == "true": get_ResourceEnvironmentProperties(clusterID);
    if CONFIG['cluster']['Websphere_variables'] == "true": get_variables(clusterID);
    if CONFIG['cluster']['Shared_libraries'] == "true": get_sharedLibraryProperties(clusterID);
    dataOut({'tagname': "resources", 'tagtype': "2"});
    dataOut({'tagname': "cluster", 'tagtype': "2"});
  dataOut({'tagname': "clusters", 'tagtype': "2"});

#===========================================================================
# loop over applications
if CONFIG['general']['application'] == "true":
  dataOut({'tagname': "applications", 'description': "Applications", 'tagtype': "1"});
  dataOut({'tagname': "enterpriseapplications", 'description': "Enterprise Applications", 'tagtype': "1"});
  for appName in cybcon_was.get_applications():
    appID = AdminConfig.getid('/Deployment:' + appName + '/');
    deplObjectID = cybcon_was.showAttribute(appID, 'deployedObject');
    dataOut({'name': "appname", 'value': appName, 'description': "Application name", 'tagname': "appname", 'tagtype': "1"});
    if CONFIG['application']['targetMapping'] == "true" or CONFIG['application']['runState'] == "true":
      get_enterpriseApplicationTargetAndState(appName, CONFIG['application']['targetMapping'], CONFIG['application']['runState']);
    if CONFIG['application']['startupBehavior'] == "true": get_enterpriseApplicationStartupBehavior(deplObjectID);
    if CONFIG['application']['binaries'] == "true": get_enterpriseApplicationBinaries(appName, deplObjectID);
    if CONFIG['application']['classLoader'] == "true": get_enterpriseApplicationClassloading(deplObjectID);
    if CONFIG['application']['requestDispatcher'] == "true": get_enterpriseApplicationRequestDispatcher(deplObjectID);
    if CONFIG['application']['sharedLibRef'] == "true": get_enterpriseApplicationLibraryReferences(deplObjectID);
    if CONFIG['application']['sessionManagement'] == "true": get_enterpriseApplicationSessionManagement(deplObjectID);
    if CONFIG['application']['jSPAndJSFoptions'] == "true": get_enterpriseApplicationJSPandJSFoptions(appName, deplObjectID);
    dataOut({'tagname': "appname", 'tagtype': "2"});
  dataOut({'tagname': "enterpriseapplications", 'tagtype': "2"});
  dataOut({'tagname': "applications", 'tagtype': "2"});

#===========================================================================
# loop over nodes
if CONFIG['general']['node'] == "true": dataOut({'tagname': "nodes", 'tagtype': "1"});
for nodeName in cybcon_was.get_nodeNames():
  nodeID = AdminConfig.getid('/Cell:' + cellName + '/Node:' + nodeName + '/');
  if CONFIG['general']['node'] == "true":
    dataOut({'name': "Node", 'value': nodeName, 'description': "WAS node", 'tagname': "node", 'tagtype': "1"});
    if CONFIG['node']['WAS_version'] == "true":
      dataOut({'name': "NodeBaseProductVersion", 'value': AdminTask.getNodeBaseProductVersion('[-nodeName ' + nodeName + ']'), 'description': "Product version", 'tagname': "property"});
    if CONFIG['node']['OS_name'] == "true":
      dataOut({'name': "NodePlatformOS", 'value': AdminTask.getNodePlatformOS('[-nodeName ' + nodeName + ']'), 'description': "Running on Operating System", 'tagname': "property"});
    if CONFIG['node']['hostname'] == "true":
      dataOut({'name': "hostName", 'value': cybcon_was.showAttribute(nodeID, 'hostName'), 'description': "Hostname", 'tagname': "hostname"});
    # ----------------------------------------------
    # put in here node specific configurations
    # ----------------------------------------------
    dataOut({'description': "Resources (node level)", 'tagname': "resources", 'tagtype': "1"});
    if CONFIG['node']['JMS_provider'] == "true": get_JMSProviderProperties(nodeID);
    if CONFIG['node']['JDBC_provider'] == "true": get_JDBCProviderProperties(nodeID);
    if CONFIG['node']['ResourceAdapter'] == "true": get_ResourceAdapterProperties(nodeID);
    if CONFIG['node']['AsyncBeans'] == "true": get_AsyncBeans(nodeID);
    if CONFIG['node']['CacheInstances'] == "true": get_CacheInstances(nodeID);
    if CONFIG['node']['Mail_provider'] == "true": get_MailProviderProperties(nodeID);
    if CONFIG['node']['URL_provider'] == "true": get_URLProviderProperties(nodeID);
    if CONFIG['node']['ResourceEnv'] == "true": get_ResourceEnvironmentProperties(nodeID);
    dataOut({'tagname': "resources", 'tagtype': "2"});
    dataOut({'description': "Environment (node level)", 'tagname': "environment", 'tagtype': "1"});
    if CONFIG['node']['Websphere_variables'] == "true": get_variables(nodeID);
    if CONFIG['node']['Shared_libraries'] == "true": get_sharedLibraryProperties(nodeID);
    if CONFIG['node']['NameSpaceBindings'] == "true":
      dataOut({'description': "Naming", 'tagname': "naming", 'tagtype': "1"});
      get_nameSpaceBindingProperties(nodeID);
      dataOut({'tagname': "naming", 'tagtype': "2"});
    dataOut({'tagname': "environment", 'tagtype': "2"});
    #===========================================================================
  # loop over servers per node
  for serverEntry in AdminConfig.list('ServerEntry' , nodeID).split(lineSeparator):
    if serverEntry == "":
      dataOut({'description': "WARNING", 'value': "No servers found in node. Skip node!"});
      continue;
    serverName = cybcon_was.showAttribute(serverEntry, "serverName" );
    serverID = AdminConfig.getid('/Cell:' + cellName + '/Node:' + nodeName + '/Server:' + serverName + '/');
    if serverID == -1:
      dataOut({'description': "WARNING", 'value': "No server configuration ID found. Skip server!"});
      continue;
    serverType = cybcon_was.showAttribute(serverID, "serverType" );
    # ----------------------------------------------
    # put in here deployment manager specific configurations
    # ----------------------------------------------
    if serverType == "DEPLOYMENT_MANAGER":
      if CONFIG['general']['dmgr'] == "true":
        dataOut({'name': "Server", 'value': serverName, 'description': "server", 'tagname': "server", 'tagprops': [ "serverType='" + serverType + "'"], 'tagtype': "1"});
        if CONFIG['dmgr']['JVM_properties'] == "true": get_JVMPropertiesFromServer(serverID);
        if CONFIG['dmgr']['EndPointPorts'] == "true": get_endPointPortsFromServer(serverEntry);
        if CONFIG['dmgr']['DCSTransports'] == "true":  get_DCSTransportsFromServer(serverID);
        if CONFIG['dmgr']['HAManagerService'] == "true": get_HAManagerServiceProperties(serverID);
        if CONFIG['dmgr']['Logging'] == "true": get_troubleshootingProperties(serverID);
        dataOut({'tagname': "server", 'tagtype': "2"});
    # ----------------------------------------------
    # put in here node agent specific configurations
    # ----------------------------------------------
    elif serverType == "NODE_AGENT":
      if CONFIG['general']['nodeagent'] == "true":
        dataOut({'name': "Server", 'value': serverName, 'description': "server", 'tagname': "server", 'tagprops': [ "serverType='" + serverType + "'"], 'tagtype': "1"});
        if CONFIG['nodeagent']['JVM_properties'] == "true": get_JVMPropertiesFromServer(serverID);
        if CONFIG['nodeagent']['EndPointPorts'] == "true": get_endPointPortsFromServer(serverEntry);
        if CONFIG['nodeagent']['DCSTransports'] == "true":  get_DCSTransportsFromServer(serverID);
        if CONFIG['nodeagent']['HAManagerService'] == "true": get_HAManagerServiceProperties(serverID);
        if CONFIG['nodeagent']['Sync_service'] == "true": get_nodeAgentSyncServiceProperties(nodeName);
        if CONFIG['nodeagent']['Logging'] == "true": get_troubleshootingProperties(serverID);
        dataOut({'tagname': "server", 'tagtype': "2"});
    # ----------------------------------------------
    # put in here application server specific configurations
    # ----------------------------------------------
    elif serverType == "APPLICATION_SERVER":
      if CONFIG['general']['appserver'] == "true":
        dataOut({'name': "Server", 'value': serverName, 'description': "server", 'tagname': "server", 'tagprops': [ "serverType='" + serverType + "'"], 'tagtype': "1"});
        if CONFIG['appserver']['ApplicationServerProperties'] == "true": get_appServerProperties(serverID, serverName);
        if CONFIG['appserver']['JVM_properties'] == "true": get_JVMPropertiesFromServer(serverID);
        if CONFIG['appserver']['EndPointPorts'] == "true": get_endPointPortsFromServer(serverEntry);
        if CONFIG['appserver']['DCSTransports'] == "true":  get_DCSTransportsFromServer(serverID);
        if CONFIG['appserver']['MSGListenerPorts'] == "true": get_MSGListenerServicePropertiesFromServer(serverID, serverName);
        if CONFIG['appserver']['HAManagerService'] == "true": get_HAManagerServiceProperties(serverID);
        dataOut({'description': "Resources (server level)", 'tagname': "resources", 'tagtype': "1"});
        if CONFIG['appserver']['JMS_provider'] == "true": get_JMSProviderProperties(serverID);
        if CONFIG['appserver']['JDBC_provider'] == "true": get_JDBCProviderProperties(serverID);
        if CONFIG['appserver']['ResourceAdapter'] == "true": get_ResourceAdapterProperties(serverID);
        if CONFIG['appserver']['AsyncBeans'] == "true": get_AsyncBeans(serverID);
        if CONFIG['appserver']['CacheInstances'] == "true": get_CacheInstances(serverID);
        if CONFIG['appserver']['Mail_provider'] == "true": get_MailProviderProperties(serverID);
        if CONFIG['appserver']['URL_provider'] == "true": get_URLProviderProperties(serverID);
        if CONFIG['appserver']['ResourceEnv'] == "true": get_ResourceEnvironmentProperties(serverID);
        dataOut({'tagname': "resources", 'tagtype': "2"});
        dataOut({'description': "Environment (server level)", 'tagname': "environment", 'tagtype': "1"});
        if CONFIG['appserver']['Websphere_variables'] == "true": get_variables(serverID);
        if CONFIG['appserver']['Shared_libraries'] == "true": get_sharedLibraryProperties(serverID);
        if CONFIG['appserver']['NameSpaceBindings'] == "true":
          dataOut({'description': "Naming", 'tagname': "naming", 'tagtype': "1"});
          get_nameSpaceBindingProperties(serverID);
          dataOut({'tagname': "naming", 'tagtype': "2"});
        if CONFIG['appserver']['Logging'] == "true": get_troubleshootingProperties(serverID);
        dataOut({'tagname': "environment", 'tagtype': "2"});
        dataOut({'tagname': "server", 'tagtype': "2"});
    # ----------------------------------------------
    # put in here webserver specific configurations
    # ----------------------------------------------
    elif serverType == "WEB_SERVER":
      if CONFIG['general']['webserver'] == "true":
        dataOut({'name': "Server", 'value': serverName, 'description': "server", 'tagname': "server", 'tagprops': [ "serverType='" + serverType + "'"], 'tagtype': "1"});
        if CONFIG['webserver']['WebServerProperties'] == "true": get_webServerProperties(serverEntry, serverID);
        if CONFIG['webserver']['Logging'] == "true":  get_webServerLogging(serverID);
        if CONFIG['webserver']['Plugin_properties'] == "true":  get_webServerPlugin(serverID);
        if CONFIG['webserver']['RemoteWebServerMgmnt'] == "true":  get_webServerRemoteMgmnt(serverEntry, serverID);
        if CONFIG['webserver']['EndPointPorts'] == "true": get_endPointPortsFromServer(serverEntry);
        dataOut({'description': "Environment (server level)", 'tagname': "environment", 'tagtype': "1"});
        if CONFIG['webserver']['Websphere_variables'] == "true": get_variables(serverID);
        dataOut({'tagname': "environment", 'tagtype': "2"});
        dataOut({'tagname': "server", 'tagtype': "2"});
    else:
      dataOut({'name': "Server", 'value': serverName, 'description': "server", 'tagname': "server", 'tagprops': [ "serverType='" + serverType + "'"], 'tagtype': "1"});
      dataOut({'tagname': "server", 'tagtype': "2"});
  if CONFIG['general']['node'] == "true": dataOut({'tagname': "node", 'tagtype': "2"});
if CONFIG['general']['node'] == "true": dataOut({'tagname': "nodes", 'tagtype': "2"});
if CONFIG['general']['cell'] == "true": dataOut({'tagname': "cell", 'tagtype': "2"});


#===========================================================================
# END

dataOut({'tagname': "configuration", 'tagtype': "2"});
dataOut({'tagname': "foot", 'tagtype': "1"});
dataOut({'tagname': "meta", 'name': "date", 'value': time.strftime("%Y-%m-%d %H:%M:%S"), 'description': "WebSphere configuration crawler ends successfully at", 'tagtype': "3"});
endTime = time.time();
elapsedTime = str("%.2f" % (endTime - startTime));
dataOut({'tagname': "meta", 'name': "elapsedTime", 'value': elapsedTime, 'unit': "seconds", 'description': "Script runtime", 'tagtype': "3"});
dataOut({'tagname': "foot", 'tagtype': "2"});
dataOut({'tagname': "configcrawler", 'tagtype': "2"});
