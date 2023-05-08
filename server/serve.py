import bentoml

runner = bentoml.pytorch.get("my_torch_model").to_runner()

svc = bentoml.Service(name="test_service", runners=[runner])

@svc.api(input=JSON(), output=JSON())
async def predict(json_obj):
    batch_ret = await runner.async_run([json_obj])
    return batch_ret[0]