#!/bin/env python

### Version of submission ###
submitVersion = "testL1"



defaultArgs   = ['isMC=False','doEleID=False','doPhoID=False','doTrigger=True', 'GT=94X_dataRun2_ReReco_EOY17_v6']
#mainOutputDir = '/store/user/tomc/tnpTuples/%s' % submitVersion # Change to your own
mainOutputDir = '/store/group/phys_egamma/lfinco/2017/L1Matching/%s' % submitVersion
from WMCore.Configuration import Configuration
from CRABClient.UserUtilities import config
config = config()

config.General.requestName            = '' 
config.General.transferLogs           = False
config.JobType.pluginName             = 'Analysis'

config.JobType.psetName               = '../../python/TnPTreeProducer_cfg.py'
config.JobType.sendExternalFolder     = True

config.Data.inputDataset              = ''
config.Data.inputDBS                  = 'global'
config.Data.publication               = False
config.Data.allowNonValidInputDataset = True
config.Site.storageSite               = 'T2_CH_CERN'#'T2_BE_IIHE' 


  
if __name__ == '__main__':

  import urllib, os, glob
  def download(url, destination):
    try:    os.makedirs(destination)
    except: pass
    urllib.urlretrieve(url, os.path.join(destination, url.split('/')[-1])) 

  from FWCore.PythonUtilities.LumiList import LumiList
  def subtractLumis(json, jsonToSubtract):
    print 'Subtracting %s from %s' % (jsonToSubtract, json)
    lumis = LumiList(filename = json) - LumiList(filename = jsonToSubtract)
    lumis.writeJSON(fileName=json)

  def mergeLumis(json, jsonToMerge):
    print 'Merging %s into %s' % (jsonToMerge, json)
    lumis = LumiList(filename = json) + LumiList(filename = jsonToMerge)
    lumis.writeJSON(fileName=json)

  def getSeedsForDoubleEle(year): # note: only getting DoubleEle seeds here
    prescalePage = 'https://tomc.web.cern.ch/tomc/triggerPrescales/%s/' % year
    hltTrigger   = 'HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL'
    dirToStore   = os.path.join('prescaleInformation', year, hltTrigger)
    download(prescalePage + hltTrigger + '.php', dirToStore)
    with open(os.path.join(dirToStore, hltTrigger + '.php')) as f:
      for line in f:
        if 'prescale1' in line and 'L1_DoubleEG' in line:
          download(prescalePage + line.split('>')[0].split('=')[-1], dirToStore)

    jsonForThresholds = {}
    for json in glob.glob(os.path.join(dirToStore, '*.json')):
      leg1 = int(json.split('L1_DoubleEG_')[-1].split('_')[0].replace('LooseIso', ''))
      leg2 = int(json.split('L1_DoubleEG_')[-1].split('_')[1].replace('LooseIso', ''))
      if (leg1, leg2) in jsonForThresholds: mergeLumis(jsonForThresholds[(leg1, leg2)], json) # this theshold pair already exists, so we merge them into the existing one
      else:                                 jsonForThresholds[(leg1, leg2)] = json

    thresholdsToSubtract = []
    for thresholds in sorted(jsonForThresholds.keys()):  # sorting from low to high thresholds
      print
      print 'Preparing json for thresholds %s' % str(thresholds)
      json = jsonForThresholds[thresholds]
      for t in thresholdsToSubtract:
        subtractLumis(json, jsonForThresholds[t])
      if not len(LumiList(filename = json)):
        print "empty json"
        continue
      yield thresholds[0], thresholds[1], json
      thresholdsToSubtract.append(thresholds)


  from CRABAPI.RawCommand import crabCommand
  from CRABClient.ClientExceptions import ClientException
  from httplib import HTTPException

  # We want to put all the CRAB project directories from the tasks we submit here into one common directory.
  # That's why we need to set this parameter (here or above in the configuration file, it does not matter, we will not overwrite it).
  config.General.workArea = 'crab_%s' % submitVersion

  def submit(config, sample, leg1threshold, leg2threshold, json):
    print  sample.split('/')[-2] + '_%s' % json.split('L1_DoubleEG_')[-1].split('_prescale')[0]
    config.General.requestName  = sample.split('/')[-2] + '_%s' % json.split('L1_DoubleEG_')[-1].split('_prescale')[0]
    config.Data.inputDataset    = sample
    config.Data.outLFNDirBase   = '%s/%s/' % (mainOutputDir,'data')
    config.Data.splitting       = 'LumiBased'
    config.Data.lumiMask        = json
    config.Data.unitsPerJob     = 100
    config.JobType.pyCfgParams  = defaultArgs + ['L1Threshold=%s' % leg1threshold]

    try:
      crabCommand('submit', config = config)
    except HTTPException as hte:
      print "Failed submitting task: %s" % (hte.headers)
    except ClientException as cle:
      print "Failed submitting task: %s" % (cle)

  for leg1, leg2, json in getSeedsForDoubleEle('2017'):
    print leg1, leg2, json
      # Crab fails on this on second iteration, of course with only a very cryptic error message
    # Not sure how to workaround this
    #submit(config, '/SingleElectron/Run2017B-31Mar2018-v1/MINIAOD', leg1, leg2, json)
    #submit(config, '/SingleElectron/Run2017C-31Mar2018-v1/MINIAOD', leg1, leg2, json)
    #submit(config, '/SingleElectron/Run2017D-31Mar2018-v1/MINIAOD', leg1, leg2, json)
    #submit(config, '/SingleElectron/Run2017E-31Mar2018-v1/MINIAOD', leg1, leg2, json)
    #submit(config, '/SingleElectron/Run2017F-31Mar2018-v1/MINIAOD', leg1, leg2, json)
  



   
