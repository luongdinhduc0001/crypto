from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,GT,pair
from charm.toolbox.secretutil import SecretUtil
from charm.toolbox.ABEncMultiAuth import ABEncMultiAuth
from charm.toolbox.symcrypto import AuthenticatedCryptoAbstraction
from charm.core.math.pairing import hashPair as sha2

class DACMACS(object):
    def __init__(self, groupObj):
        self.util = SecretUtil(groupObj, verbose=False)  #Create Secret Sharing Scheme
        self.group = groupObj    #:Prime order group
    
    def setup(self):
        '''Global Setup (executed by CA)'''
        #:In global setup, a bilinear group G of prime order p is chosen
        #:The global public parameters, GP and p, and a generator g of G. A random oracle H maps global identities GID to elements of G
    
        #:group contains 
        #:the prime order p is contained somewhere within the group object
        g = self.group.random(G1)
        #: The oracle that maps global identities GID onto elements of G
        #:H = lambda str: g** group.hash(str)
        H = lambda x: self.group.hash(x, G1)
        a = self.group.random()
        g_a = g ** a
        GPP = {'g': g, 'g_a': g_a, 'H': H}
        GMK = {'a': a}
        
        return (GPP, GMK)

    
    def registerUser(self, GPP):
        '''Generate user keys (executed by the user).'''
        g = GPP['g']
        u = self.group.random()
        z = self.group.random()
        g_u = g ** u
        g_z = g ** (1 / z)
        
        return ((g_u, z), { 'g_z': g_z, 'u': u }) # (private, public)

    
    def setupAuthority(self, GPP, authorityid, attributes, authorities):
        '''Generate attribute authority keys (executed by attribute authority)'''
        if authorityid not in authorities:
            alpha = self.group.random()
            beta = self.group.random()
            gamma = self.group.random()
            SK = {'alpha': alpha, 'beta': beta, 'gamma': gamma}
            PK = {
                'e_alpha': pair(GPP['g'], GPP['g']) ** alpha,
                'g_beta_inv': GPP['g'] ** (1/beta),
                'g_beta_gamma': GPP['g'] ** (gamma/beta)
            }
            authAttrs = {}
            authorities[authorityid] = (SK, PK, authAttrs)
        else:
            SK, PK, authAttrs = authorities[authorityid]
        for attrib in attributes:
            if attrib in authAttrs:
                continue
            versionKey = self.group.random() # random or really 'choose' ?
            h = GPP['H'](attrib)
            pk = ((GPP['g'] ** versionKey) * h) ** SK['gamma']
            authAttrs[attrib] = {
                'VK': versionKey, #secret
                'PK': pk, #public
            }
        return (SK, PK, authAttrs)

     
    def keygen(self, GPP, authority, attribute, userObj, USK = None):
        '''Generate user keys for a specific attribute (executed on attribute authority)'''
        if 't' not in userObj:
            userObj['t'] = self.group.random() #private to AA
        t = userObj['t']
        
        ASK, APK, authAttrs = authority
        u = userObj
        if USK is None:
            USK = {}
        if 'K' not in USK or 'L' not in USK or 'R' not in USK or 'AK' not in USK:
            USK['K'] = \
                (u['g_z'] ** ASK['alpha']) * \
                (GPP['g_a'] ** u['u']) * \
                (GPP['g_a'] ** (t / ASK['beta']))
            USK['L'] = u['g_z'] ** (ASK['beta'] * t)
            USK['R'] = GPP['g_a'] ** t
            USK['AK'] = {}
        AK = (u['g_z'] ** (ASK['beta'] * ASK['gamma'] * t)) * \
            (authAttrs[attribute]['PK'] ** (ASK['beta'] * u['u']))
        USK['AK'][attribute] = AK
        return USK

    
    def __encrypt(self, GPP, policy_str, k, authority):
        '''Generate the cipher-text from the content(-key) and a policy (executed by the content owner)'''
        #GPP are global parameters
        #k is the content key (group element based on AES key)
        #policy_str is the policy string
        #authority is the authority tuple
        
        _, APK, authAttrs = authority
        
        policy = self.util.createPolicy(policy_str)
        secret = self.group.random()
        shares = self.util.calculateSharesList(secret, policy)
        shares = dict([(x[0].getAttributeAndIndex(), x[1]) for x in shares])
        
        C1 = k * (APK['e_alpha'] ** secret)
        C2 = GPP['g'] ** secret
        C3 = APK['g_beta_inv'] ** secret
        C = {}
        D = {}
        DS = {}
        
        for attr, s_share in shares.items():
            k_attr = self.util.strip_index(attr)
            r_i = self.group.random()
            attrPK = authAttrs[attr]
            C[attr] = (GPP['g_a'] ** s_share) * ~(attrPK['PK'] ** r_i)
            D[attr] = APK['g_beta_inv'] ** r_i
            DS[attr] = ~(APK['g_beta_gamma'] ** r_i)
        
        return {'C1': C1, 'C2': C2, 'C3': C3, 'C': C, 'D': D, 'DS': DS, 'policy': policy_str}

    
    def generateTK(self, GPP, CT, UASK, g_u):
        '''Generates a token using the user's attribute secret keys to offload the decryption process (executed by cloud provider)'''
        usr_attribs = list(UASK['AK'].keys())
        policy = self.util.createPolicy(CT['policy'])
        pruned = self.util.prune(policy, usr_attribs)
        if pruned == False:
            return False
        coeffs = self.util.getCoefficients(policy)
        
        dividend = pair(CT['C2'], UASK['K']) * ~pair(UASK['R'], CT['C3'])
        n_a = 1
        divisor = 1
        
        for attr in pruned:
            x = attr.getAttributeAndIndex()
            y = attr.getAttribute()
            temp = \
                pair(CT['C'][y], g_u) * \
                pair(CT['D'][y], UASK['AK'][y]) * \
                pair(CT['DS'][y], UASK['L'])
            divisor *= temp ** (coeffs[x] * n_a)
        return dividend / divisor

    
    def __decrypt(self, CT, TK, z):
        '''Decrypts the content(-key) from the cipher-text using the token and the user secret key (executed by user/content consumer)'''
        return CT['C1'] / (TK ** z)

    def __random_key(self):
        return self.group.random(GT)

    def encrypt(self, GPP, policy_str, M, authority):
        if type(M) != bytes and type(policy_str) != str:
            raise Exception("message and policy not right type!")
        k = self.__random_key()
        c1 = self.__encrypt(GPP, policy_str, k, authority)
        # instantiate a symmetric enc scheme from this key
        cipher = AuthenticatedCryptoAbstraction(sha2(k))
        c2 = cipher.encrypt(M)
        return { 'c1':c1, 'c2':c2 }
    
    def decrypt(self, ct, TK, z):
        c1, c2 = ct['c1'], ct['c2']
        key = self.__decrypt(c1, TK, z)
        if key is False:
            raise Exception("failed to decrypt!")
        cipher = AuthenticatedCryptoAbstraction(sha2(key))
        return cipher.decrypt(c2)

    def ukeygen(self, GPP, authority, attribute, userObj):
        '''Generate update keys for users and cloud provider (executed by attribute authority?)'''
        ASK, _, authAttrs = authority
        oldVersionKey = authAttrs[attribute]['VK']
        newVersionKey = oldVersionKey
        while oldVersionKey == newVersionKey:
            newVersionKey = self.group.random()
        authAttrs[attribute]['VK'] = newVersionKey
        
        u = userObj['u']
        
        AUK = ASK['gamma'] * (newVersionKey - oldVersionKey)
        KUK = GPP['g'] ** (u * ASK['beta'] * AUK)
        CUK = ASK['beta'] * AUK / ASK['gamma']
        
        authAttrs[attribute]['PK'] = authAttrs[attribute]['PK'] * (GPP['g'] ** AUK)
        
        return { 'KUK': KUK, 'CUK': CUK }

    
    def skupdate(self, USK, attribute, KUK):
        '''Updates the user attribute secret key for the specified attribute (executed by non-revoked user)'''
        USK['AK'][attribute] = USK['AK'][attribute] * KUK

    
    def ctupdate(self, GPP, CT, attribute, CUK):
        '''Updates the cipher-text using the update key, because of the revoked attribute (executed by cloud provider)'''
        CT['C'][attribute] = CT['C'][attribute] * (CT['DS'][attribute] ** CUK)


def basicTest():
    print("RUN basicTest")
    groupObj = PairingGroup('SS512')
    dac = DACMACS(groupObj)
    GPP, GMK = dac.setup()
        
    users = {} # public user data
    authorities = {}
    
    authorityAttributes = ["ONE", "TWO", "THREE", "FOUR"]
    authority1 = "authority1"
    
    dac.setupAuthority(GPP, authority1, authorityAttributes, authorities)
    
    alice = { 'id': 'alice', 'authoritySecretKeys': {}, 'keys': None }
    alice['keys'], users[alice['id']] = dac.registerUser(GPP)
    
    for attr in authorityAttributes[0:-1]:
        dac.keygen(GPP, authorities[authority1], attr, users[alice['id']], alice['authoritySecretKeys'])

    k = b'Hello World!'
    print("k:", k)

    policy_str = '((ONE or THREE) and (TWO or FOUR))'
    print(alice)
    print(users)
    CT = dac.encrypt(GPP, policy_str, k, authorities[authority1])
    
    TK = dac.generateTK(GPP, CT['c1'], alice['authoritySecretKeys'], alice['keys'][0])
    
    PT = dac.decrypt(CT, TK, alice['keys'][1])
    print("PT:", PT)
    # print "k", k
    # print "PT", PT
    
    assert k == PT, 'FAILED DECRYPTION!'
    print('SUCCESSFUL DECRYPTION')

def dacmacs_setup():
    groupObj = PairingGroup('SS512')
    dac = DACMACS(groupObj)
    GPP, GMK = dac.setup()
    return dac, GPP, GMK

if __name__ == '__main__':
    basicTest()
    # test()