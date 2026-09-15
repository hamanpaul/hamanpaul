import hashlib,json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1]
REV='ec017919d4fa5770bca8e859e369518c71f4eb1c'

def ev(repo,first,last=None,claim='公開 README 宣告的責任與接點'):
    path='docs/evidence/'+repo+'/README.md'
    lines=(R/path).read_text().splitlines(keepends=True)
    a=next(i for i,l in enumerate(lines) if first in l)
    b=next((i for i in range(a,len(lines)) if last in lines[i]),a) if last else a
    return {'path':path,'line':a+1,'end_line':b+1,'excerpt_sha256':hashlib.sha256(''.join(lines[a:b+1]).encode()).hexdigest(),'claim':claim}
E={
 'claw':ev('paulshaclaw','> **Fact:**'),
 'claw-cortex':ev('paulshaclaw','### 已遷移','## 本 repo 目前聚焦'),
 'hippo':ev('paulsha-hippo','> **Fact:**'),
 'hippo-flow':ev('paulsha-hippo','pipeline：'),
 'claw-hippo':ev('paulshaclaw','vendors -->|transcripts|','shell -->|memory-facing'),
 'cortex':ev('paulsha-cortex','> **Fact:**'),
 'cortex-agent':ev('paulsha-cortex','persona 是 manager'),
 'policy':ev('paulsha-conventions','> **Fact:**'),
 'policy-agent':ev('paulsha-conventions','- **Agent checklist**'),
 'tp':ev('testpilot-core','> **Scope:**'),
 'tp-plugin':ev('testpilot-core','- `examples/sample_echo/`','maintained separately'),
 'tp-advisory':ev('testpilot-core','Tier-2 is reached only','verification gate passed'),
 'uart-use':ev('testpilot-core','Workflow-specific dependencies'),
 'sw':ev('serialwrap','> **Fact:**'),
 'sw-device':ev('serialwrap','`serialwrapd` owns','remain coordinated.'),
 'loggen':ev('log-generator','This toolkit runs','boot-time fault injector.'),
 'mud':ev('paulsha-patchmud','- 量測閉環','- 排名資料流'),
 'mud-agent':ev('paulsha-patchmud','- CLI-based adapter'),
}
def sorted_ev(*keys):
    return sorted([E[k] for k in keys],key=lambda x:(x['path'],x['line'],x['end_line']))
C=[]
def node(id,label,kind,sub,resp,*keys,tag=None):
    d=dict(id=id,label=label,type=kind,sublabel=sub,responsibility=resp,basis='declared',evidence=sorted_ev(*keys))
    if tag:d['tag']=tag
    C.append(d)
node('claw','paulshaclaw','frontend','操作入口／Shell','人類操作、產品介面與整合入口；不擁有工作生命週期、領域 verdict 或長期經驗的最終裁決权。','claw',tag='入口')
node('cortex','paulsha-cortex','backend','工作生命週期／派工','治理 work、WorkflowRun、Job、Slice、retry、review 與 delivery；Persona 是角色契約，AgentInstance 才是執行個體。','cortex','cortex-agent',tag='生命週期')
node('executor','外部 Agent／CLI','external','受約束的執行與補全','Cortex 派工的 AgentInstance、TestPilot 選配建議與 PatchMUD adapter 使用的外部模型執行能力；這是能力類別，不表示同一行程、共用憑證或同一部署。','cortex-agent','mud-agent','tp-advisory',tag='執行者')
node('hippo','paulsha-hippo','database','經驗記憶／來源與歸因','管理 outcome-linked 經驗生命週期、session 蒸餾、recall、applied attribution、reinforce、contradict、retire；不是派工控制器。','hippo','hippo-flow',tag='經驗')
node('policy','paulsha-conventions','security','Repo policy／變更完整性','規範文件、版號、分支、PR、generated facts 與 policy drift；deterministic enforcement 不等於領域測試裁決。','policy',tag='規範')
node('testpilot','testpilot-core','backend','測試生命週期／證據','Plugin-based host；core-owned 路徑執行測試、保存 evidence/trace 與 plugin 評估產生的 canonical verdict。可選 Agent 建議不代表測試通過。','tp',tag='驗證')
node('plugin','領域 Plugin','backend','案例／環境／evaluate','各專案自行定義案例、環境操作與評估語意。公開例子包括 sample_echo 與 serialwrap_reliability；並非所有 plugin 都需要硬體。','tp','tp-plugin','uart-use',tag='領域語意')
node('serialwrap','serialwrap','messagebus','UART 仲裁／原始證據','serialwrapd 擁有裝置 session 與真實 UART，提供 single-writer 仲裁、WAL、recovery 與薄 CLI/console clients。','sw','sw-device',tag='實體證據')
node('hardware','DUT／真實硬體','external','UART 裝置','現有 UART/device 工作流程的真實測試對象；不代表 TestPilot 的所有領域都必須使用硬體。','sw-device','uart-use',tag='現場')
node('log-generator','log-generator','backend','重啟耐久／故障注入','透過 serialwrap 做 reboot-log soak tests；每個 selector 一個 controller，異常目標須先安裝 fault injector。不是純模擬日誌產生器。','loggen',tag='測試工具')
node('patchmud','paulsha-patchmud','backend','凍結關卡／確定性評分','獨立評測實驗室；frozen fixtures、可重播評分、排名無 LLM 裁判，對 Cortex/Hippo 零 runtime 依賴。','mud','mud-agent',tag='實驗室')
L=[]
def edge(id,a,b,label,*keys,variant='default'):
    L.append(dict(id=id,**{'from':a,'to':b},label=label,variant=variant,basis='declared',evidence=sorted_ev(*keys)))
edge('claw-cortex','claw','cortex','控制 client／CLI','claw-cortex',variant='emphasis')
edge('claw-hippo','claw','hippo','記憶整合','claw-hippo')
edge('cortex-executor','cortex','executor','受治理派工','cortex','cortex-agent',variant='emphasis')
edge('executor-hippo','executor','hippo','Session／recall','claw-hippo','hippo-flow')
edge('policy-executor','policy','executor','提供變更規範','policy-agent',variant='security')
edge('patchmud-executor','patchmud','executor','評測補全','mud-agent',variant='dashed')
edge('testpilot-executor','testpilot','executor','選配恢復建議','tp-advisory',variant='dashed')
edge('testpilot-plugin','testpilot','plugin','執行／evaluate','tp',variant='emphasis')
edge('plugin-serialwrap','plugin','serialwrap','限 UART 工作流程','tp-plugin','uart-use',variant='dashed')
edge('log-generator-serialwrap','log-generator','serialwrap','重啟壓測','loggen')
edge('serialwrap-hardware','serialwrap','hardware','獨占 UART','sw-device',variant='emphasis')
F=dict(schema_version=1,document_type='architecture-facts',repository=dict(url='https://github.com/hamanpaul/hamanpaul',revision=REV),scope=dict(name='公開工程生態的責任與契約接點',includes=['公開核心 repo 的責任界線','來源 README 明確宣告的操作、派工、記憶與測試接點','真實硬體與外部 executor 能力類別'],excludes=['未驗證的全自動端到端閉環','私有 repo 內容','每個 repo 的內部生命週期展開','bootstrap 範本與社群預設檔案（保留於 README 矩陣）']),components=sorted(C,key=lambda x:x['id']),boundaries=[],relations=sorted(L,key=lambda x:x['id']),unknowns=[dict(id='deployment-e2e',question='這些公開契約是否已在同一部署完成從診斷到交付再回灌的完整驗證？',impact='本圖不是一次成功 runtime E2E 的證明，也不宣稱 Cortex 直接呼叫所有 domain tools。'),dict(id='experience-outcomes',question='每次修補是否都有可追溯 applied attribution 與後續結果？',impact='不能把所有 session 蒸餾或 recall 視為已證實有效的經驗。'),dict(id='routing-consumption',question='PatchMUD 匯出是否已被部署中的 Cortex routing 自動採納？',impact='不畫出 PatchMUD 到 Cortex 的已接通 runtime/routing 邊。')],conflicts=[])
(R/'docs/facts.json').write_text(json.dumps(F,ensure_ascii=False,indent=2)+'\n')
positions={'hippo':(50,80),'claw':(400,80),'cortex':(750,80),'policy':(1100,80),'patchmud':(50,350),'executor':(750,350),'testpilot':(1100,350),'hardware':(50,620),'serialwrap':(400,620),'log-generator':(750,620),'plugin':(1100,620)}
IR={'meta':{'title':'Paul Haman｜受治理的工程生態','quality_profile':'showcase','repository':dict(F['repository'],provider='github'),'viewBox':[0,0,1400,810]},'components':[],'connections':[],'cards':[{'dot':'cyan','title':'責任分開，證據串接','items':['Cortex 管工作；Plugin 定義領域判定','虛線為選配／特定用途，不是必經鏈']},{'dot':'amber','title':'契約地圖，不是 E2E 證書','items':['來源：固定版本的公開 README','完整閉環、經驗效益仍需實測']} ]}
for c in F['components']:
    n={k:c[k] for k in ('id','label','type','sublabel','tag') if k in c}
    n.update(pos=list(positions[c['id']]),size=[240,96],sources=[{k:e[k] for k in ('path','line','end_line')} for e in c['evidence'][:3]])
    IR['components'].append(n)
for e in F['relations']:IR['connections'].append({k:e[k] for k in ('id','from','to','label','variant')})
(R/'docs/index.json').write_text(json.dumps(IR,ensure_ascii=False,indent=2)+'\n')

# Apply the reviewed semantic caption and native layout corrections. Temporary seeding only.
F['components'][0]['responsibility']=F['components'][0]['responsibility'].replace('权','權')
ls=(R/'docs/evidence/paulsha-hippo/README.md').read_text().splitlines(keepends=True)
i=next(i for i,l in enumerate(ls) if '日常命令：' in l)
x=next(e for e in F['relations'] if e['id']=='executor-hippo')
x['evidence'].append({'path':'docs/evidence/paulsha-hippo/README.md','line':i+1,'end_line':i+1,'excerpt_sha256':hashlib.sha256(ls[i].encode()).hexdigest(),'claim':'提供跨 CLI recall 檢索與 applied attribution 命令。'})
x['evidence'].sort(key=lambda a:(a['path'],a['line'],a['end_line']))
next(e for e in F['relations'] if e['id']=='claw-cortex')['label']='client／CLI'
IR['schema_version']=1;IR['diagram_type']='architecture';IR['meta']['viewBox']=[1050,608]
e={x['id']:x for x in IR['connections']}
e['claw-cortex']['label']='client／CLI'
e['plugin-serialwrap'].update(fromSide='bottom',toSide='bottom',via=[[1220,765],[520,765]])
e['cortex-executor']['labelAt']=[870,260]
e['testpilot-plugin']['labelAt']=[1220,530]
e['executor-hippo'].update(fromSide='bottom',toSide='bottom',via=[[870,510],[680,510],[680,260],[170,260]])
for c in IR['components']:
    c['pos']=[v*.75 for v in c['pos']];c['size']=[v*.75 for v in c['size']]
for x in IR['connections']:
    if 'labelAt' in x:x['labelAt']=[v*.75 for v in x['labelAt']]
    if 'via' in x:x['via']=[[v*.75 for v in xy] for xy in x['via']]
e['testpilot-executor']['labelDy']=28
(R/'docs/facts.json').write_text(json.dumps(F,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(R/'docs/index.json').write_text(json.dumps(IR,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
