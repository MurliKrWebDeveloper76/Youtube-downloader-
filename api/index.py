import os
import sys
import subprocess
import json
import yt_dlp
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# The cookies provided by the user
COOKIES_CONTENT = """# Netscape HTTP Cookie File
# http://curl.haxx.se/rfc/cookie_spec.html
# This is a generated file!  Do not edit.

.youtube.com	TRUE	/	TRUE	1777181553	VISITOR_INFO1_LIVE	r6zRVDh6ky8
.youtube.com	TRUE	/	TRUE	1777181553	VISITOR_PRIVACY_METADATA	CgJJThIEGgAgVg%3D%3D
.youtube.com	TRUE	/	TRUE	1785732416	VISITOR_INFO1_LIVE	jsw_NOre7Vo
.youtube.com	TRUE	/	TRUE	1785732416	VISITOR_PRIVACY_METADATA	CgJJThIEGgAgEA%3D%3D
.youtube.com	TRUE	/	TRUE	1771390166	VISITOR_INFO1_LIVE	sEGfRvP9t7c
.youtube.com	TRUE	/	TRUE	1771390166	VISITOR_PRIVACY_METADATA	CgJJThIEGgAgGA%3D%3D
.youtube.com	TRUE	/	TRUE	1771390183	VISITOR_INFO1_LIVE	NJfsBG4SAXo
.youtube.com	TRUE	/	TRUE	1771390183	VISITOR_PRIVACY_METADATA	CgJJThIEGgAgOA%3D%3D
.youtube.com	TRUE	/	TRUE	1775755747	VISITOR_INFO1_LIVE	78YwXijY8HQ
.youtube.com	TRUE	/	TRUE	1775755747	VISITOR_PRIVACY_METADATA	CgJJThIEGgAgRg%3D%3D
.youtube.com	TRUE	/	TRUE	1771390138	__Secure-ROLLOUT_TOKEN	CImfzNGHsOvSfBCD8pDSm5KPAxj14Nfkzp2PAw%3D%3D
.youtube.com	TRUE	/	TRUE	1771390183	__Secure-ROLLOUT_TOKEN	CPuRyeC8pdXdkgEQjfLw9JuSjwMYkLWQ-s6djwM%3D
.youtube.com	TRUE	/	TRUE	1785422480	VISITOR_INFO1_LIVE	No1t507NDDI
.youtube.com	TRUE	/	TRUE	1785422480	VISITOR_PRIVACY_METADATA	CgJJThIEGgAgWA%3D%3D
.youtube.com	TRUE	/	TRUE	1786879867	VISITOR_INFO1_LIVE	78YwXijY8HQ
.youtube.com	TRUE	/	TRUE	1786879867	VISITOR_PRIVACY_METADATA	CgJJThIEGgAgRg%3D%3D
.youtube.com	TRUE	/	TRUE	1785423056	VISITOR_INFO1_LIVE	Vb_cSKm07Q4
.youtube.com	TRUE	/	TRUE	1785423056	VISITOR_PRIVACY_METADATA	CgJJThIEGgAgXQ%3D%3D
.youtube.com	TRUE	/	TRUE	1773116646	__Secure-YNID	12.YT=irtNVhvu8xw6LvKvIP98q3pVF_D5-IzYbLWVL-hXPl1L-NIOmM6z9jFFs31ED2nub1qW-xVfT7iN_advPd1-IZin1_bULzt5vh5OWZ3AoxjiGLIVakMq6S8Pw46CvsGVdQeceGDRIQRdBBxo-xKUmjV4_7iyKhqDYzP3U0cYZoSPu7hqvsko8SQrcKNfmf5qYoMcECs04_HHS7S-4UsRCs-Hfn-vLFqg1X89E3vK8ESTRWE4a82cMnD2gfz4tvBu-3h7Vta0CMFW_WLPW_id-dVuoh-6zCoKI74Lc_Ii53a2o-DQsGAwvHzjp-lfXMHNBjsCEvZQTXcQXO4a8_uaMQ
.youtube.com	TRUE	/	TRUE	1773677000	VISITOR_INFO1_LIVE	ZBl9EL86Kkg
.youtube.com	TRUE	/	TRUE	1773677000	VISITOR_PRIVACY_METADATA	CgJJThIEGgAgYQ%3D%3D
.youtube.com	TRUE	/	TRUE	1773281678	__Secure-ROLLOUT_TOKEN	CLH1rOzfke7MlwEQ3MKMqdXUjwMY3MKMqdXUjwM%3D
.youtube.com	TRUE	/	TRUE	1773281678	VISITOR_INFO1_LIVE	-EItrGYq2rk
.youtube.com	TRUE	/	TRUE	1773281678	VISITOR_PRIVACY_METADATA	CgJJThIEGgAgZQ%3D%3D
.youtube.com	TRUE	/	TRUE	1773461098	VISITOR_INFO1_LIVE	ti3EF-QyFPI
.youtube.com	TRUE	/	TRUE	1773461098	VISITOR_PRIVACY_METADATA	CgJJThIEGgAgWw%3D%3D
.youtube.com	TRUE	/	TRUE	1773460447	__Secure-ROLLOUT_TOKEN	CJyfkfPU5a_9YxDpqIek79mPAxjIzZml79mPAw%3D%3D
.youtube.com	TRUE	/	TRUE	1773676752	__Secure-ROLLOUT_TOKEN	CMmkgdTwkNSt1gEQ3rGSwu7PjwMY8d2eipXgjwM%3D
.youtube.com	TRUE	/	TRUE	1805887882	PREF	tz=Asia.Calcutta&f7=100&f4=4000000&f6=40000000
www.youtube.com	FALSE	/	FALSE	1794386910	QUESTION_AI_UUID	ed27f10b-9dc4-4ab1-a2b0-0f7781698c55
www.youtube.com	FALSE	/	FALSE	1794558167	QUESTION_AI_PCUID	p3in6hi1zzuwn94v18mfjywb2z675f_1759826913
.youtube.com	TRUE	/	TRUE	1775755709	__Secure-ROLLOUT_TOKEN	CLfrkvWn89iHnAEQmJWMwpmbjwMYpc6R59WckAM%3D
.youtube.com	TRUE	/	TRUE	1775755709	__Secure-YNID	12.YT=E_BVwhAzMh9B0k0AlQEic8f4PykemKCsD5hOxMHDbz8Q5pS6oSrpQrBFGblyv13lkKvYweBxNyCltKKl5Axyhn54_K2QggfnkKBXwtRpeQmQqf0L1UMOv_agQKVB1MkmTTw06ZYNRT8toQ9VaCRHa14AOA2UdZnDVk9giWfg1_pejqLcZfG9vhP-ZJ9rFcmCpbMTvq78P-4nRdUgDdFAPAR-unpC6b6sKDd_R7GRZhHIgWGf9jk-NbBx22cyFF7HFCHqhD879Wxkk6YZahDL5N-gtYy7JU3AR1FvK1-tL870UvCGbwiGXz0URNc8mtCEQcIr6VeF2PwbIdKqL5Y5pA
.youtube.com	TRUE	/	TRUE	1775988941	VISITOR_INFO1_LIVE	elmpGgALvrg
.youtube.com	TRUE	/	TRUE	1775988941	VISITOR_PRIVACY_METADATA	CgJJThIEGgAgMQ%3D%3D
.youtube.com	TRUE	/	TRUE	1775985138	__Secure-ROLLOUT_TOKEN	CMDs2diky5K6iAEQoJDDv6yjkAMYisHmv6yjkAM%3D
.youtube.com	TRUE	/	TRUE	1777181553	__Secure-ROLLOUT_TOKEN	CPLfwLzAqNHuexDPuqqKzoWPAxiylti9lcaQAw%3D%3D
.youtube.com	TRUE	/	TRUE	1777617082	VISITOR_INFO1_LIVE	Z1C_hC0LNms
.youtube.com	TRUE	/	TRUE	1777617082	VISITOR_PRIVACY_METADATA	CgJJThIEGgAgVA%3D%3D
.youtube.com	TRUE	/	TRUE	1777532302	__Secure-ROLLOUT_TOKEN	CJLa37PPsrhbEN3b0I6w0JADGM_tppCw0JAD
.youtube.com	TRUE	/	TRUE	1778504651	VISITOR_INFO1_LIVE	86a842UzIrA
.youtube.com	TRUE	/	TRUE	1778504651	VISITOR_PRIVACY_METADATA	CgJJThIEGgAgVQ%3D%3D
.youtube.com	TRUE	/	TRUE	1778753353	__Secure-ROLLOUT_TOKEN	CI3B7YWg1u2kzwEQwsfVtNbskAMY-qS98vTzkAM%3D
.youtube.com	TRUE	/	TRUE	1780290370	VISITOR_INFO1_LIVE	ODLEm1ZPAoY
.youtube.com	TRUE	/	TRUE	1780290370	VISITOR_PRIVACY_METADATA	CgJJThIEGgAgSQ%3D%3D
.youtube.com	TRUE	/	TRUE	1779001914	VISITOR_INFO1_LIVE	ZzIpj3CCxdw
.youtube.com	TRUE	/	TRUE	1779001914	VISITOR_PRIVACY_METADATA	CgJJThIEGgAgZA%3D%3D
.youtube.com	TRUE	/	TRUE	1779001915	__Secure-ROLLOUT_TOKEN	CKv_2p3iz4OVNRCA3dvtkvuQAxj81qjukvuQAw%3D%3D
.youtube.com	TRUE	/	TRUE	1780290370	__Secure-ROLLOUT_TOKEN	COz41rbF083UHRC6xam7vfaQAxj1pdXd0qCRAw%3D%3D
.youtube.com	TRUE	/	TRUE	1780324880	VISITOR_INFO1_LIVE	N_s4cUOMVyw
.youtube.com	TRUE	/	TRUE	1780324880	VISITOR_PRIVACY_METADATA	CgJJThIEGgAgYQ%3D%3D
.youtube.com	TRUE	/	TRUE	1780324904	__Secure-ROLLOUT_TOKEN	CKvR8au3qYf-YhDn3Zml06GRAxiM2Ouw06GRAw%3D%3D
.youtube.com	TRUE	/	TRUE	1784005516	VISITOR_INFO1_LIVE	R9aRKu59Ozg
.youtube.com	TRUE	/	TRUE	1784005516	VISITOR_PRIVACY_METADATA	CgJJThIEGgAgDg%3D%3D
.youtube.com	TRUE	/	TRUE	1784005516	__Secure-YNID	15.YT=ctgeSlOWr9e4wFY99UBO_eqyf6FQLYcOoYBarlHD8kEAltHXDm4FnRiDXQ9om4a0jeWlmRMcbEIy6Pszaiu23B4s-3GkP-cI3-pTTFS39rvDBIZT1I_D0zMF0VFynfrFaOOGQTNJ3EEZsTryCt2V3HyJfgFt7EqByNJskU6osjOYZ74pRLTBwsIq9F3o0rxwmU3WJ8CHAEwpTfE1J9aKqaf5KUIUFrKU7PXbxvDeLWC8o580gLLE7F-W6xHBVKC-KKBmbmPFpVqckMw9ouvQeea9I2d-HqqIuY1xugk7Oww_OjKhxd7i2jYNrLRYhD3WvSq8bRJ_Tv7VnD_i13bKqA
.youtube.com	TRUE	/	TRUE	1784005930	__Secure-ROLLOUT_TOKEN	CJPOjenK7O-ipQEQz9n-3OKMkgMYvsC0ouSMkgM%3D
.youtube.com	TRUE	/	TRUE	1785770310	VISITOR_INFO1_LIVE	1ZFIr2_PV0w
.youtube.com	TRUE	/	TRUE	1785770310	VISITOR_PRIVACY_METADATA	CgJJThIEGgAgUw%3D%3D
.youtube.com	TRUE	/	TRUE	1780153042	__Secure-YNID	15.YT=VV-Bd0qASuEL2s79K4COeeZminMy-X4H04BY4QAXFX9XmArdFpR3G7yHIpw9uhjQ5rhxuAgwsFruAYGSDPa3QeG_sxRcL_fZuMIR-qS85Jdp20hy_6brMTzAIHTkY40mLY1yvgUN51SCbIpL1-yE5phKPFHQs5MFDOWlIm6ae_D9imNAt8g0qR_nHbYwjmdJBu_4XAWhY10snkCLWcqC_FbEYIutd97-f1aRePFbJUJT1dHSwffvI1FErKD9Wb-G9ODbPdM8om7YR4zGxrVIGJQ8bxmq_H092FatUe_Mr2yWpoIQgdNelIw0QvpQLekjT4I4swS38lFKZZCdPJfqWQ
.youtube.com	TRUE	/	TRUE	1784973929	VISITOR_INFO1_LIVE	uX2v31UTgIw
.youtube.com	TRUE	/	TRUE	1784973929	VISITOR_PRIVACY_METADATA	CgJJThIEGgAgZA%3D%3D
.youtube.com	TRUE	/	TRUE	1784973929	__Secure-YNID	15.YT=SUubqvVEDAc5XXHFaCTXrAz1mgUlgaOctGyMiUUwWVJNlzVWp4teMKI5VOMpy9Fchsz8l728oicrRHA3ikkArNbeh-HtaQ-2S9r2C6In48Og-xgekNxQYUVUWUxD7c45qSn8DCK1ZL12na94U4Mg65t2_8qt33aZRyl-r1rmV5iOY3Bbaa100CDGmse4HWtGIWe3OlRglCP4jR_-9i3Aah8Xsj5Sph2F9_JBNgqZ1siWIbPN5p8GqQzfIidrd0eK0L7dX04P36tNx_dUsxi4mX3ikgNJqhXyO8Zc0ReYvGX4ddntXLP1U16m4vPkP7MbQ4B2PYPsoBq4El5PGiaspg
.youtube.com	TRUE	/	TRUE	1784986386	__Secure-ROLLOUT_TOKEN	CLuO9--9qIPAzgEQ_cbJrPqokgMY26a14KipkgM%3D
.youtube.com	TRUE	/	TRUE	1785340666	VISITOR_INFO1_LIVE	RktBTqwD6RA
.youtube.com	TRUE	/	TRUE	1785340666	VISITOR_PRIVACY_METADATA	CgJJThIEGgAgHA%3D%3D
.youtube.com	TRUE	/	TRUE	1785340666	__Secure-YNID	15.YT=g2KNVwmjAJbvCjcvk_MEnSrEV5d0gAqvfAEpwyNnN6IvlJzObChT810hBHIR3xX5dAvEBi31anxrVA6Rw0DmFDxqKTQXwwrJtjJEVDlJ9m6lOXrjf2GkApFsawx6qaPnX0Rb1nHYRVWfX-1DXppQT5Ee4FzgFI98p8jS9u21wBcJ5m4-V8NQCQ1PlZr7lrp4Odw26vYHpNpbxvi2nwXX1w4UOuvJLBILdADfkkQK5_yySlSqB5pLtsMR1RL6uKR5yoNKPHqT80UmruP3rvSz14Sll718pdWFgVz6CLMtGrGVt9DxMzbzCYKE-KTP9_xdCrW95fA4zBKQC2SDxDfJPA
.youtube.com	TRUE	/	TRUE	1785340666	__Secure-ROLLOUT_TOKEN	CL6V4_ii5omlogEQrJLmtq2pkgMY98i5xtCzkgM%3D
.youtube.com	TRUE	/	TRUE	1785422480	__Secure-ROLLOUT_TOKEN	CLLFzquNtIOOIBDZhOyI5LePAxixqNiqgbaSAw%3D%3D
.youtube.com	TRUE	/	TRUE	1785422482	__Secure-YNID	15.YT=exJyS9uVvUc0mcTxnMTA2qhXIBgwdc1W6RvGLh-yVDwISp8plrdBIzEBFeg3H6Ww2DkSVhHzH7toodWElLj__T0Ms4V-9jqZdOScUhJmNOgT2757njVAylCbplIasql8CRqfw2cTWuIxo5joDJTJWKVWc1u8KQFsl63rIv7f-6xc8JXVmwfXu7obeDkE_ex-vo2fYz_u0tpJsrhxqIE4KdSFOchB5U47uhfyXvDTSXR-dwK8YLAz39vrCV5St2R5PYOHal4uOgCjpkH7kdj26Fj-TR52ZapXL874sGfufrauj2DKcKAme0dIIPG5XA9u4iu6MPkgPtXHZWcJzeqfMA
.youtube.com	TRUE	/	TRUE	1785423053	__Secure-ROLLOUT_TOKEN	CNX7kIzt0uOauwEQycyGmM_IjwMYrOj4u4O2kgM%3D
.youtube.com	TRUE	/	TRUE	1785423054	__Secure-YNID	15.YT=e_PzJ6sQ0DSzsrwzZPA60RLq50sLK1vGjYjRpwiVpnTacYP1dVaA6PVG25xlXVV96ofQEynweyovMYmNGTpSnkCnNpWB23X32_5W1V_niBkLr-kFPNyoMFfsFSVV8uvxBnXupbD1H4F0v2JwjbWw4XSpeA8qXiwtP4qZ_LSNpqkPS-wEI-cZm42Q28m06QXoKbwDkdxOy-Ivn8E1orcUHk3jdIVSG7rf1UeIIqE7kRGhzxQF_fZZSY71K1M3IcPOK-OTycxZ_fM87YhECbSC4lPAd2FFL-Wfts-yHWi15Q_hTnTdjP0m0kypeiy1nwWh6KlJejT5drNh2AOaXhDkQw
.youtube.com	TRUE	/	TRUE	1785731577	__Secure-ROLLOUT_TOKEN	CMDIgPPTldjvhAEQwPqgoLCUkgMYmY-a54C_kgM%3D
.youtube.com	TRUE	/	TRUE	1785732008	__Secure-ROLLOUT_TOKEN	CMb40IOGm8vBGxDtj_KJnI2PAxis5ti0gr-SAw%3D%3D
.youtube.com	TRUE	/	TRUE	1786768715	VISITOR_INFO1_LIVE	iRB36F3LvWA
.youtube.com	TRUE	/	TRUE	1786768715	VISITOR_PRIVACY_METADATA	CgJJThIEGgAgGQ%3D%3D
.youtube.com	TRUE	/	TRUE	1786879845	__Secure-YNID	16.YT
.youtube.com	TRUE	/	TRUE	1786768714	__Secure-YNID	16.YT=aGZbmYyCiOSOtFXWAy5TYB9iZNx_YtaCmN6hu_jgN_BFs3sZ4_R8fpxLX-B69Y_3C6zW-ivFDaPZLwiVKOiCA_-wEtqlZ13d6M08QU7BMdp_pqtfh2Bn4cdos-KRBCOKoxQonwUVJszQASivakruAKpB9qe4SPY5jqASADLMUCik-Jo4ov-swIoz9hPBElQrSBkxqyBHHU1LPFqDjC8f5nB7n078P_L_Bas624WPaw6ZTsp-3K0yef8KJx3IKO38we5ytsevCyE1fevbpDT1akC-uGNuA641lQFC3nu6LsUGhGfCTreFWeCVwaso0wLcc9aJ5Un3CJPpwvSGdmwlVQ
.youtube.com	TRUE	/	TRUE	1786768715	__Secure-ROLLOUT_TOKEN	CI7jzYWd2uusxAEQpdHjuJjdkgMY1oCQuZjdkgM%3D
.youtube.com	TRUE	/	TRUE	1771329636	GPS	1
.youtube.com	TRUE	/	TRUE	0	YSC	c-EpFOd_cpA
.youtube.com	TRUE	/	TRUE	1786879836	__Secure-ROLLOUT_TOKEN	CMDIgPPTldjvhAEQwPqgoLCUkgMYzNb-s7bgkgM%3D
.youtube.com	TRUE	/	TRUE	0	YSC	c-EpFOd_cpA
.youtube.com	TRUE	/	TRUE	1786879836	__Secure-ROLLOUT_TOKEN	CMDIgPPTldjvhAEQwPqgoLCUkgMYzNb-s7bgkgM%3D
.youtube.com	TRUE	/	TRUE	1786879868	VISITOR_INFO1_LIVE	78YwXijY8HQ
.youtube.com	TRUE	/	TRUE	1786879868	VISITOR_PRIVACY_METADATA	CgJJThIEGgAgRg%3D%3D
.youtube.com	TRUE	/	FALSE	1805887864	HSID	ApIe4yWI4gxg9AVFL
.youtube.com	TRUE	/	TRUE	1805887864	SSID	AOFBBtc01fTC_WTgG
.youtube.com	TRUE	/	FALSE	1805887864	APISID	Y42a_-5ds8lGkOEa/AaYsF0F5N07bcQ1vk
.youtube.com	TRUE	/	TRUE	1805887864	SAPISID	dAlFXN9Kax-E9bKg/Ang5pvZ90zWNV8Q-6
.youtube.com	TRUE	/	TRUE	1805887864	__Secure-1PAPISID	dAlFXN9Kax-E9bKg/Ang5pvZ90zWNV8Q-6
.youtube.com	TRUE	/	TRUE	1805887864	__Secure-3PAPISID	dAlFXN9Kax-E9bKg/Ang5pvZ90zWNV8Q-6
.youtube.com	TRUE	/	FALSE	1805887864	SID	g.a0006wgVK1CeJww2lSzIqrU5udbYCIdpqOX5KSoKHwcOKhf32tE-vPHMd7bsbWPZWrYN62fBHQACgYKAcoSARYSFQHGX2MiWOL4kqyojt83Omoth5n2KxoVAUF8yKr59FPbD33L8estgTJDQI6H0076
.youtube.com	TRUE	/	TRUE	1805887864	__Secure-1PSID	g.a0006wgVK1CeJww2lSzIqrU5udbYCIdpqOX5KSoKHwcOKhf32tE-2D8ezJkhiIrBR5JGrHquAAACgYKAe8SARYSFQHGX2MikL-X62wzfyJl2JSEZGvxyRoVAUF8yKr2wSEvISDBvz1SGReAoVce0076
.youtube.com	TRUE	/	TRUE	1805887864	__Secure-3PSID	g.a0006wgVK1CeJww2lSzIqrU5udbYCIdpqOX5KSoKHwcOKhf32tE-LFRLSlHAdiyHMiqriwwL_wACgYKARUSARYSFQHGX2Mi3Sn9imWfD_9TEJgdLEqUHhoVAUF8yKrcJSCWuw-Te2Nvn0RYOkhY0076
.youtube.com	TRUE	/	TRUE	1802863865	__Secure-1PSIDTS	sidts-CjQBBj1CYl4D1r1JIKNALiqSk7y5babZkdkL0UAihnuQ8-AyP_o9CH0G16LV3bPJquZK4ecIEAA
.youtube.com	TRUE	/	TRUE	1802863865	__Secure-3PSIDTS	sidts-CjQBBj1CYl4D1r1JIKNALiqSk7y5babZkdkL0UAihnuQ8-AyP_o9CH0G16LV3bPJquZK4ecIEAA
.youtube.com	TRUE	/	TRUE	1805887864	LOGIN_INFO	AFmmF2swRQIgaSzAg7cwcuAd0G8jbCFIkmWPbnp6RtdKR_gr9dVrZJcCIQDThZwMT-E8F5NEAcxZ5LBI0EPe2e-FqeooOAcSjF2wMA:QUQ3MjNmd0NLVEp1eF9GVjFZRlFCaGpuaHJ0ZHNFSzA1dUJJZ1RVQWw3Ni1FeUF5V3BzOWwzMGJSMGhQWjRULUNVbjFuR2ZYUGxtdzZ2TW9ZMTc5UXZsdE9TVHRycVN5YVBNTzM1OWpvRWVaSVlFZV9HakJieEJ1ZWNEYmlNMG4xUHFpUFFUTGZYN0FkUjI4STEtanFpT3p2TFEzUUJ3XzVR
.youtube.com	TRUE	/	FALSE	1802863885	SIDCC	AKEyXzW9Rob32cJYKaAz4aosjt9JNbJ1sTQD_b83JYlLdYnqCk1T-NVUxRi9H1xQfMcXZp4aSA
.youtube.com	TRUE	/	TRUE	1802863885	__Secure-1PSIDCC	AKEyXzUv-rlGxLj6zzmuYJyLivhwSTuiF9yxYhMkfhSPT1_YBCjp2BpW35YkX0eGCr6ZSb6v
.youtube.com	TRUE	/	TRUE	1802863885	__Secure-3PSIDCC	AKEyXzXEWg5zZo8lwM_hOFZrfyyZUW1oZIlN7cxlUTArbymXhVPs4tofHKOXBVLHKSNXZN_PCQ"""

# Writable location for cookies on Vercel
TEMP_COOKIES_PATH = '/tmp/cookies.txt'

def ensure_cookies():
    """Writes cookie content to /tmp to avoid Read-only FS errors on Vercel."""
    try:
        with open(TEMP_COOKIES_PATH, 'w') as f:
            f.write(COOKIES_CONTENT)
        return TEMP_COOKIES_PATH
    except Exception as e:
        print(f"Error writing cookies: {e}")
        return None

# Standard browser headers
BROWSER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

@app.route('/api/video_info', methods=['POST', 'OPTIONS'])
def video_info():
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"}), 200
        
    try:
        data = request.get_json(silent=True)
        if not data or 'url' not in data:
            return jsonify({"error": "YouTube URL is required."}), 400
            
        url = data['url']
        cookies = ensure_cookies()
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'user_agent': BROWSER_HEADERS['User-Agent'],
            'cookiefile': cookies,
            'no_cache_dir': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                return jsonify({"error": "Video not found."}), 404
            
            return jsonify({
                "id": info.get('id'),
                "title": info.get('title'),
                "author": info.get('uploader') or info.get('channel', 'Unknown'),
                "duration": f"{info.get('duration', 0) // 60}:{info.get('duration', 0) % 60:02d}",
                "views": f"{info.get('view_count', 0):,}",
                "thumbnailUrl": info.get('thumbnail'),
                "url": url
            })
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/available_resolutions', methods=['POST'])
def available_resolutions():
    try:
        data = request.get_json(silent=True)
        url = data.get('url')
        if not url:
            return jsonify({"error": "URL required"}), 400
            
        cookies = ensure_cookies()
        ydl_opts = {
            'quiet': True,
            'nocheckcertificate': True,
            'user_agent': BROWSER_HEADERS['User-Agent'],
            'cookiefile': cookies,
            'no_cache_dir': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            
            res_set = set()
            for f in formats:
                # Strictly look for progressive MP4s (video + audio in one file)
                # This ensures we don't need ffmpeg for merging on Vercel.
                if (f.get('vcodec') != 'none' and 
                    f.get('acodec') != 'none' and 
                    f.get('ext') == 'mp4'):
                    res = f.get('height')
                    if res:
                        res_set.add(f"{res}p")
            
            return jsonify({
                "progressive": sorted(list(res_set), key=lambda x: int(x.replace('p', ''))),
                "audio": ["128kbps", "192kbps", "320kbps"]
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/download')
def download():
    """
    ULTRA DIRECT PIPE (Progressive Only):
    Streams binary data directly. Prioritizes single-file MP4s to avoid 
    ffmpeg dependencies in serverless environments.
    """
    video_id = request.args.get('id')
    res_req = request.args.get('resolution', '720p')
    format_type = request.args.get('type', 'mp4')
    
    if not video_id:
        return "Video ID required", 400

    video_url = f"https://www.youtube.com/watch?v={video_id}"
    height = res_req.replace('p', '')
    cookies = ensure_cookies()
    
    if format_type == 'mp3':
        # Best audio available as a single file
        format_spec = 'bestaudio[ext=m4a]/bestaudio/best'
    else:
        # PROGRESSIVE-FIRST SELECTION LOGIC:
        # 1. Best progressive MP4 with height <= requested
        # 2. Best progressive MP4 overall
        # 3. Best overall single file
        format_spec = f'best[height<={height}][ext=mp4][vcodec!=none][acodec!=none]/best[ext=mp4][vcodec!=none][acodec!=none]/best'

    def generate():
        cmd = [
            sys.executable, "-m", "yt_dlp",
            '-f', format_spec,
            '--no-playlist',
            '--no-warnings',
            '--nocheckcertificate',
            '--no-cache-dir',
            '--user-agent', BROWSER_HEADERS['User-Agent'],
            '--cookies', cookies,
            '-o', '-',  # Stream binary to stdout
            video_url
        ]
        
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        
        try:
            while True:
                chunk = proc.stdout.read(1024 * 512) 
                if not chunk:
                    break
                yield chunk
        finally:
            proc.terminate()

    try:
        ydl_opts = {'quiet': True, 'cookiefile': cookies, 'no_cache_dir': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            title = info.get('title', 'video')
    except:
        title = "video"

    safe_title = "".join([c for c in title if c.isalnum() or c in ('-', '_')])[:50]
    filename = f"YT_Ultra_{safe_title}.{format_type}"

    headers = {
        'Content-Type': 'application/octet-stream',
        'Content-Disposition': f'attachment; filename="{filename}"',
        'X-Content-Type-Options': 'nosniff',
        'Cache-Control': 'no-cache',
    }

    return Response(stream_with_context(generate()), headers=headers)

if __name__ == "__main__":
    app.run(port=5000)
