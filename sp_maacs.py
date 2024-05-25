from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,GT,pair
from charm.toolbox.secretutil import SecretUtil
from charm.toolbox.ABEncMultiAuth import ABEncMultiAuth
from bls import BLS01
from charm.toolbox.symcrypto import AuthenticatedCryptoAbstraction
from charm.core.math.pairing import hashPair as sha2

class SPMAACS(ABEncMultiAuth):
    def __init__(self, groupObj):
        self.util = SecretUtil(groupObj, verbose=False)  #Create Secret Sharing Scheme
        self.group = groupObj    #:Prime order group

    def setup(self):
        signer = BLS01(groupObj=self.group)
        GPP = ""
        return GPP
    
    def CASetup(self, GPP):
        MPK = ""
        MSK = ""
        return (MPK, MSK)
    
    def AASetup(self, GPP, k, Uk):
        APKk = ""
        ASKk = ""
        return (APKk, ASKk)
    
    def CAKeygen(self, GPP, uid):
        CAPKgid  = ""
        CASKgid = ""
        return (CAPKgid, CASKgid)
    
    def AAKeygen(self, Sgidk, GPP, MPK, CAPKgid, ASKk):
        ASKSgidk = ""
        return ASKSgidk
    
    def __encrypt(self, k, policy_str, GPP, APK):
        CT = ""
        return CT
    
    def __decrypt(self, CT, GPP, FKgid):
        K = ""
        return K
    
    def __random_key(self):
        return self.group.random(GT)

    def encrypt(self, M, policy_str, GPP, APK):
        if type(M) != bytes and type(policy_str) != str:
            raise Exception("message and policy not right type!")
        k = self.__random_key()
        c1 = self.__encrypt(k, policy_str, GPP, APK)
        # instantiate a symmetric enc scheme from this key
        cipher = AuthenticatedCryptoAbstraction(sha2(k))
        c2 = cipher.encrypt(M)
        return { 'c1':c1, 'c2':c2 }
    
    def decrypt(self, ct, GPP, FKgid):
        c1, c2 = ct['c1'], ct['c2']
        key = self.__decrypt(GPP, c1, FKgid)
        if key is False:
            raise Exception("failed to decrypt!")
        cipher = AuthenticatedCryptoAbstraction(sha2(key))
        return cipher.decrypt(c2)
    
def test():
    print("RUN basicTest")
    groupObj = PairingGroup('SS512')
    dac = SPMAACS(groupObj)
