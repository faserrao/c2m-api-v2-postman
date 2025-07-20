source scripts/python_env/e2o.venv/bin/activate
pip install -r scripts/python_env/requirements.txt
python scripts/ebnf_to_openapi_ch_v7.py ./DataDictionary/c2m-api-dd_v3_withComments_v4.ebnf ./openapi/c2m_openapi_spec_final_new.yaml
