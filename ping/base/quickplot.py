#!/usr/bin/python

import numpy as np
from matplotlib import pyplot as plt

data = np.array([

[0.462921351194,0.303614467382]  ,[0.459550559521,0.28493976593]  ,[0.453932583332,0.275301218033]  ,[0.446067422628,0.263855427504]  ,[0.437078654766,0.252409636974]  ,[0.42471909523,0.240361452103]  ,[0.412359535694,0.22831325233]  ,[0.398876398802,0.217469885945]  ,[0.386516839266,0.207831323147]  ,[0.374157309532,0.201204821467]  ,[0.362921357155,0.195783138275]  ,[0.351685404778,0.192771077156]  ,[0.3404494524,0.190361440182]  ,[0.329213470221,0.189156621695]  ,[0.266292124987,0.190361440182]  ,[0.253932595253,0.192771077156]  ,[0.241573035717,0.196987956762]  ,[0.231460675597,0.201807230711]  ,[0.221348315477,0.209036141634]  ,[0.212359547615,0.216265067458]  ,[0.204494386911,0.224096387625]  ,[0.196629211307,0.232530117035]  ,[0.192134827375,0.242771089077]  ,[0.187640443444,0.253614455462]  ,[0.185393258929,0.265662640333]  ,[0.184269666672,0.27831324935]  ,[0.183146074414,0.291566252708]  ,[0.184269666672,0.333734929562]  ,[0.186516851187,0.348795175552]  ,[0.18988764286,0.363855421543]  ,[0.194382026792,0.378915667534]  ,[0.20000000298,0.394578307867]  ,[0.206741571426,0.412650614977]  ,[0.214606747031,0.431927710772]  ,[0.225842699409,0.451807230711]  ,[0.238202244043,0.47349396348]  ,[0.253932595253,0.495783120394]  ,[0.270786523819,0.51807230711]  ,[0.287640452385,0.541566252708]  ,[0.30561798811,0.565060257912]  ,[0.323595494032,0.587349414825]  ,[0.341573029757,0.609638571739]  ,[0.358426958323,0.631325304508]  ,[0.371910125017,0.651807248592]  ,[0.385393261909,0.669879496098]  ,[0.397752821445,0.685542166233]  ,[0.407865166664,0.698795199394]  ,[0.415730327368,0.709036171436]  ,[0.4202247262,0.715662658215]  ,[0.453932583332,0.308433741331]  ,[0.452808976173,0.307831317186]  ,[0.450561791658,0.294578313828]  ,[0.452808976173,0.262048184872]  ,[0.455056190491,0.251204818487]  ,[0.458426952362,0.240963861346]  ,[0.464044958353,0.231927707791]  ,[0.470786511898,0.222891569138]  ,[0.478651672602,0.215662643313]  ,[0.489887654781,0.20843373239]  ,[0.501123607159,0.203012049198]  ,[0.514606714249,0.198192775249]  ,[0.529213488102,0.194578319788]  ,[0.544943809509,0.191566258669]  ,[0.559550583363,0.189156621695]  ,[0.574157297611,0.187951803207]  ,[0.587640464306,0.188554212451]  ,[0.600000023842,0.189156621695]  ,[0.612359523773,0.190361440182]  ,[0.622471928596,0.193373501301]  ,[0.632584273815,0.196987956762]  ,[0.642696619034,0.201204821467]  ,[0.652808964252,0.207228913903]  ,[0.661797761917,0.214457824826]  ,[0.668539345264,0.22168675065]  ,[0.675280928612,0.230722889304]  ,[0.6808989048,0.240963861346]  ,[0.68539327383,0.251204818487]  ,[0.688764035702,0.263253003359]  ,[0.68988764286,0.275903612375]  ,[0.691011250019,0.290361434221]  ,[0.68988764286,0.305421680212]  ,[0.688764035702,0.321084350348]  ,[0.68539327383,0.337349385023]  ,[0.682022452354,0.354819267988]  ,[0.677528083324,0.372289150953]  ,[0.670786499977,0.389156639576]  ,[0.662921369076,0.407228916883]  ,[0.652808964252,0.425903618336]  ,[0.640449464321,0.444578319788]  ,[0.625842690468,0.463855415583]  ,[0.610112369061,0.483734935522]  ,[0.593258440495,0.504819273949]  ,[0.574157297611,0.527108430862]  ,[0.556179761887,0.549397587776]  ,[0.538202226162,0.572891592979]  ,[0.519101142883,0.596385538578]  ,[0.502247214317,0.618674695492]  ,[0.485393255949,0.640361428261]  ,[0.469662934542,0.658433735371]  ,[0.456179767847,0.673493981361]  ,[0.443820238113,0.684337377548]  ,[0.433707863092,0.693373501301]  ,[0.423595517874,0.699999988079]  ,[0.414606750011,0.704216837883]  ,[0.407865166664,0.706024110317] 	])

x, y = data.T

plt.gca().invert_yaxis() #because image data in webstrates origins at top left

plt.scatter(x,y)

plt.show()	