from fastapi import FastAPI, Query, HTTPException
from typing import Optional
from datetime import datetime
import math

from app.config import settings
from app.domain.mock_generator import (
    gerar_venda_completa,
    VENDEDORES_MOCK,
    PRODUTOS_MOCK,
    CLIENTES_MOCK
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
    ## 📈 Sales, Cash Flow & Commission Audit Engine
    API mock projetada para simulação de **Pipelines de Dados**, **Análise de Margem Bruta**, **Projeção de Fluxo de Caixa / Parcelamentos** e **Auditoria de Comissões por Recebimento**.
    """,
    version=settings.VERSION
)

@app.get("/", tags=["HealthCheck"])
def health_check():
    return {
        "status": "ONLINE",
        "servico": settings.PROJECT_NAME,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/vendas", tags=["Vendas & Auditoria"])
def listar_vendas(
    page: int = Query(1, ge=1, description="Número da página"),
    limit: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE, description="Registros por página"),
    vendedor_id: Optional[str] = Query(None, description="ID do vendedor (ex: VND-101)"),
    status_venda: Optional[str] = Query(None, description="FATURADO, APROVADO, EM_APROVACAO, CANCELADO"),
    status_global_recebimento: Optional[str] = Query(None, description="QUITADO, PARCIALMENTE_RECEBIDO, EM_ABERTO, INADIMPLENTE"),
    apenas_alerta_desconto: bool = Query(False, description="Filtra vendas com desconto acima do permitido"),
    apenas_alerta_margem: bool = Query(False, description="Filtra vendas onde a margem bruta de lucro foi destruída"),
    simular_erro_servidor: bool = Query(False, description="Simula erro HTTP 500 para testes de resiliência")
):
    if simular_erro_servidor:
        raise HTTPException(status_code=500, detail="[SIMULAÇÃO] Falha de comunicação com o ERP Financeiro.")

    raw_data = [gerar_venda_completa(vendedor_id_filtro=vendedor_id) for _ in range(limit)]

    data_filtrada = []
    for item in raw_data:
        if status_venda and item["status_venda"] != status_venda.upper():
            continue
        if status_global_recebimento and item["dados_faturamento"]["status_global_recebimento"] != status_global_recebimento.upper():
            continue
        if apenas_alerta_desconto and not item["comissao_auditoria"]["alerta_auditoria_desconto"]:
            continue
        if apenas_alerta_margem and not item["comissao_auditoria"]["alerta_margem_critica"]:
            continue
        data_filtrada.append(item)

    total_pages = math.ceil(settings.TOTAL_SIMULATED_RECORDS / limit)

    return {
        "meta": {
            "page": page,
            "limit": limit,
            "registros_retornados": len(data_filtrada),
            "total_registros_estimado": settings.TOTAL_SIMULATED_RECORDS,
            "total_paginas_estimado": total_pages,
            "tem_proxima_pagina": page < total_pages
        },
        "data": data_filtrada
    }

@app.get("/api/v1/vendedores", tags=["Tabelas Dimensionais"])
def listar_vendedores():
    return {"total_registros": len(VENDEDORES_MOCK), "data": VENDEDORES_MOCK}

@app.get("/api/v1/produtos", tags=["Tabelas Dimensionais"])
def listar_produtos():
    return {"total_registros": len(PRODUTOS_MOCK), "data": PRODUTOS_MOCK}

@app.get("/api/v1/clientes", tags=["Tabelas Dimensionais"])
def listar_clientes():
    return {"total_registros": len(CLIENTES_MOCK), "data": CLIENTES_MOCK}