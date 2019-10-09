from CRABClient.UserUtilities import config, getUsernameFromSiteDB
import sys
config = config()

submitVersion = "ntuple_2017_UltraLegacy"

doEleTree = 'doEleID=True'
doPhoTree = 'doPhoID=False'
doHLTTree = 'doTrigger=False'
doRECO    = 'doRECO=False'

mainOutputDir = '/store/group/phys_egamma/swmukher/UL/%s' % submitVersion

config.General.transferLogs = False

config.JobType.pluginName  = 'Analysis'

# Name of the CMSSW configuration file
config.JobType.psetName  = '/afs/cern.ch/user/s/swmukher/work/egammaNtuple/try/CMSSW_10_6_1_patch1/src/EgammaAnalysis/TnPTreeProducer/python/TnPTreeProducer_cfg.py'
config.Data.allowNonValidInputDataset = False

config.Data.inputDBS = 'global'
config.Data.publication = False

#config.Data.publishDataName = 
config.Site.storageSite = 'T2_CH_CERN'


if __name__ == '__main__':

    from CRABAPI.RawCommand import crabCommand
    from CRABClient.ClientExceptions import ClientException
    from httplib import HTTPException

    # We want to put all the CRAB project directories from the tasks we submit here into one common directory.
    # That's why we need to set this parameter (here or above in the configuration file, it does not matter, we will not overwrite it).
    config.General.workArea = 'crab_%s' % submitVersion

    def submit(config):
        try:
            crabCommand('submit', config = config)
        except HTTPException as hte:
            print "Failed submitting task: %s" % (hte.headers)
        except ClientException as cle:
            print "Failed submitting task: %s" % (cle)


    ##### now submit DATA
    config.Data.outLFNDirBase = '%s/%s/' % (mainOutputDir,'data')
    config.Data.splitting     = 'LumiBased'
    #    config.Data.lumiMask      = 'https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions17/13TeV/Final/Cert_294927-306462_13TeV_PromptReco_Collisions17_JSON.txt'
    config.Data.lumiMask      = 'https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions17/13TeV/ReReco/Cert_294927-306462_13TeV_EOY2017ReReco_Collisions17_JSON_v1.txt'
    config.Data.unitsPerJob   = 90
    config.JobType.pyCfgParams  = ['isMC=False','isAOD=False',doEleTree,doPhoTree,doHLTTree,doRECO]


    config.General.requestName  = 'SingleElectron_29Jun2019_2017UL_C_TRY4'
    config.Data.inputDataset    = '/SingleElectron/Run2017C-29Jun2019_UL2017validation-v1/MINIAOD'
    submit(config)

    config.General.requestName  = 'SingleElectron_29Jun2019_2017UL_F_TRY4'
    config.Data.inputDataset    = '/SingleElectron/Run2017F-29Jun2019_UL2017validation-v1/MINIAOD'
    submit(config)



#    config.General.requestName  = 'RunF_2017'
#    config.Data.inputDataset    = '/SingleElectron/Run2017F-17Nov2017-v1/AOD'
#    submit(config)




    
