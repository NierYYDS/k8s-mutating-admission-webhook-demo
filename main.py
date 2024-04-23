import base64
import json
import logging
import uvicorn
from fastapi import Body, FastAPI
from pydantic import BaseModel
from typing import Optional


class Response(BaseModel):
    """webhook response核心payload"""

    uid: str
    allowed: bool
    patchType: Optional[str] = None
    patch: Optional[str] = None


class AdmissionReviewResponse(BaseModel):
    """webhook请求返回数据"""

    apiVersion: str = "admission.k8s.io/v1"
    kind: str = "AdmissionReview"
    response: Response


app = FastAPI()


@app.get("/")
async def index():
    return {"message": "Hello, this is a pod labeler admissionWebhook!"}


@app.post("/mutate")
async def mutate(req=Body(...)):
    """Mutation of pod and add label foo=bar"""
    label_k, label_v = "foo", "bar"
    req_uid = req["request"]["uid"]

    logging.info(
        f"req_uid={req_uid}, Received a mutation request: {json.dumps(req, indent=2)}"
    )
    # 添加标签
    json_patch = f"""[{{"op": "add", "path": "/metadata/labels/{label_k}", "value": "{label_v}"}}]"""
    json_patch = base64.b64encode(json_patch.encode("utf-8"))

    req_pod = req["request"]["object"]
    if req_pod["kind"] != "Pod":
        logging.error(f"req_uid={req_uid}, This webhook only supports pod mutation.")
        return Response(uid=req["request"]["uid"], allowed=False)

    # 如果存在该标签，就跳过
    if label_k in req_pod["metadata"]["labels"]:
        logging.info(
            f"req_uid={req_uid}, Pod already has {label_k} label. Skip patching."
        )
        resp = Response(uid=req_uid, allowed=True)
    else:
        # 注意mutatingWebhook 拿不到metadata.name和pod uid信息
        logging.info(f"req_uid={req_uid}, Patching pod with {label_k} = {label_v}.")
        resp = Response(
            uid=req_uid,
            allowed=True,
            patchType="JSONPatch",
            patch=json_patch,
        )
    return AdmissionReviewResponse(response=resp)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    uvicorn.run(
        app,
        log_level="debug",
        host="0.0.0.0",
        ssl_ca_certs="./certs/ca.crt",
        ssl_keyfile="./certs/server.key",
        ssl_certfile="./certs/server.crt",
    )
