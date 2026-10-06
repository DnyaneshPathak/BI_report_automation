import pickle, json
from bi_automation.planning.orchestrator import PlanOrchestrator
from bi_automation.engine.executor import PlanExecutor

res = pickle.load(open('var/tmp/cache_aecd38d6-6986-421b-9d17-5855bcfc8b36.pkl', 'rb'))
df = res.df_clean
schema_card = res.schema_card

print('Schema card:')
for c in schema_card:
    print(' ', c)

print()
print('Re-running plan generation...')
prompt = (
    'show annual income vs spending score analysis using scatter plot. '
    'also give me gender distribution using count plot. '
    'for both charts show proper labels and scale.'
)

orchestrator = PlanOrchestrator()
plan = orchestrator.generate_plan(prompt, schema_card)

print('Plan items generated:', len(plan.get('items', [])))
for item in plan.get('items', []):
    iid = item.get('id')
    itype = item.get('type')
    ichart = item.get('chart')
    ititle = item.get('title')
    print('  -', iid, ':', itype, '/', 'chart=' + str(ichart), '/', 'title=' + str(ititle))

print()
print('Running executor...')
executor = PlanExecutor(df)
computed = executor.execute(plan)

print('Computed figures:')
for k, v in computed.items():
    ctype = v.get('chart_type')
    warn = v.get('warnings')
    nrows = len(v['dataset']['source']) - 1
    print('  ' + k + ': chart_type=' + str(ctype) + ', warnings=' + str(warn) + ', rows=' + str(nrows))
