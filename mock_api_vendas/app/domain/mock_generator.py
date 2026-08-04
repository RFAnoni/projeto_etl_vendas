from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from faker import Faker
import random

fake = Faker('pt_BR')

REGIONAIS = ["SP_CAPITAL", "SP_INTERIOR", "RJ_SUL", "MG_CENTRO", "SUL_RS_SC", "NE_BAHIA"]
CARGOS = ["SDR_JUNIOR", "EXECUTIVO_PLENO", "EXECUTIVO_SENIOR", "ACCOUNT_MANAGER"]
CANOES_VENDA = ["B2B_DIRECT", "INSIDE_SALES", "PARCEIRO_CANAL"]

VENDEDORES_MOCK = [
    {
        "vendedor_id": f"VND-10{i}",
        "nome": fake.name(),
        "cargo": random.choice(CARGOS),
        "regional": random.choice(REGIONAIS)
    }
    for i in range(1, 16)
]

PRODUTOS_MOCK = [
    {
        "produto_id": "PRD-001",
        "nome": "Licença ERP Cloud Express",
        "categoria": "Software",
        "classificacao_rentabilidade": "CLASSE_A_ALTA_MARGEM",
        "custo": 80.0,
        "tabela": 290.0,
        "desc_max": 15.0,
        "comissao_base_pct": 5.0,
        "margem_alvo_pct": 70.0
    },
    {
        "produto_id": "PRD-002",
        "nome": "Módulo Fiscal Automatizado",
        "categoria": "Software",
        "classificacao_rentabilidade": "CLASSE_A_ALTA_MARGEM",
        "custo": 45.0,
        "tabela": 180.0,
        "desc_max": 12.0,
        "comissao_base_pct": 4.5,
        "margem_alvo_pct": 65.0
    },
    {
        "produto_id": "PRD-003",
        "nome": "Implementação & Onboarding B2B",
        "categoria": "Serviços",
        "classificacao_rentabilidade": "CLASSE_B_MARGEM_MEDIA",
        "custo": 400.0,
        "tabela": 1200.0,
        "desc_max": 20.0,
        "comissao_base_pct": 3.5,
        "margem_alvo_pct": 50.0
    },
    {
        "produto_id": "PRD-004",
        "nome": "Leitor de Código de Barras Industrial",
        "categoria": "Hardware",
        "classificacao_rentabilidade": "CLASSE_C_COMMODITY",
        "custo": 280.0,
        "tabela": 350.0,
        "desc_max": 8.0,
        "comissao_base_pct": 2.0,
        "margem_alvo_pct": 20.0
    },
    {
        "produto_id": "PRD-005",
        "nome": "Suporte Premium 24/7 (Anual)",
        "categoria": "Serviços",
        "classificacao_rentabilidade": "CLASSE_B_MARGEM_MEDIA",
        "custo": 150.0,
        "tabela": 800.0,
        "desc_max": 25.0,
        "comissao_base_pct": 4.0,
        "margem_alvo_pct": 55.0
    }
]

CLIENTES_MOCK = [
    {"cliente_id": f"CLI-80{i}", "nome_razao_social": fake.company(), "segmento": random.choice(["Enterprise", "Mid-Market", "SMB"]), "uf": random.choice(["SP", "RJ", "MG", "PR", "RS", "BA"])}
    for i in range(1, 30)
]

CONDICOES_PAGAMENTO = {
    "A_VISTA": {"parcelas": 1, "intervalo_dias": 0},
    "30_DIAS": {"parcelas": 1, "intervalo_dias": 30},
    "30/60_DIAS": {"parcelas": 2, "intervalo_dias": 30},
    "30/60/90_DIAS": {"parcelas": 3, "intervalo_dias": 30},
    "6X_MENSAL": {"parcelas": 6, "intervalo_dias": 30},
    "12X_MENSAL": {"parcelas": 12, "intervalo_dias": 30}
}

def gerar_venda_completa(data_fixa: Optional[str] = None, vendedor_id_filtro: Optional[str] = None) -> Dict[str, Any]:
    vendedor = next((v for v in VENDEDORES_MOCK if v["vendedor_id"] == vendedor_id_filtro), random.choice(VENDEDORES_MOCK))
    produto = random.choice(PRODUTOS_MOCK)
    cliente = random.choice(CLIENTES_MOCK)

    status_venda = random.choices(["FATURADO", "APROVADO", "EM_APROVACAO", "CANCELADO"], weights=[0.75, 0.12, 0.08, 0.05])[0]

    quantidade = random.randint(1, 10)
    valor_tabela = round(produto["tabela"] * quantidade, 2)
    desconto_pct = round(random.choices([0.0, 5.0, 10.0, 15.0, 25.0], weights=[0.35, 0.30, 0.20, 0.10, 0.05])[0], 2)
    valor_praticado = round(valor_tabela * (1 - (desconto_pct / 100)), 2)

    # 1. Auditoria de Desconto
    alerta_desconto = desconto_pct > produto["desc_max"]
    motivo_alerta_desconto = f"Desconto de {desconto_pct}% excede teto ({produto['desc_max']}%)." if alerta_desconto else None

    # 2. Motor de Comissão Variável por Margem Bruta
    custo_total = produto["custo"] * quantidade
    lucro_bruto = valor_praticado - custo_total
    margem_realizada_pct = round((lucro_bruto / valor_praticado) * 100, 2) if valor_praticado > 0 else 0.0

    penalizacao_desconto_pct = round(desconto_pct * 0.15, 2)
    comissao_final_pct = max(0.5, round(produto["comissao_base_pct"] - penalizacao_desconto_pct, 2))

    alerta_margem_critica = False
    motivo_alerta_margem = None

    if margem_realizada_pct < (produto["margem_alvo_pct"] * 0.6):
        alerta_margem_critica = True
        motivo_alerta_margem = f"Margem de {margem_realizada_pct}% abaixo da mínima esperada ({produto['margem_alvo_pct']}%)."
        comissao_final_pct = 0.5 # Reduz para piso mínimo

    valor_comissao_total = round(valor_praticado * (comissao_final_pct / 100), 2) if status_venda != "CANCELADO" else 0.0

    # 3. Faturamento, Cronograma de Parcelas e Fluxo de Caixa
    dt_pedido = datetime.now() - timedelta(days=random.randint(1, 120))
    cond_chave = random.choice(list(CONDICOES_PAGAMENTO.keys()))
    config_cond = CONDICOES_PAGAMENTO[cond_chave]
    total_parc = config_cond["parcelas"]
    valor_parcela_base = round(valor_praticado / total_parc, 2)

    parcelas_cronograma = []
    valor_comissao_liberada_caixa = 0.0
    parcelas_pagas_count = 0
    parcelas_inadimplentes_count = 0

    nf_numero = f"NF-2026-{random.randint(10000, 99999)}" if status_venda == "FATURADO" else None
    nf_chave = f"352607{fake.cnpj().replace('.', '').replace('/', '').replace('-', '')}55001{random.randint(100000, 999999)}" if status_venda == "FATURADO" else None
    dt_emissao_nf = dt_pedido + timedelta(hours=random.randint(2, 24)) if status_venda == "FATURADO" else None

    if status_venda == "FATURADO":
        for i in range(1, total_parc + 1):
            dt_vencimento = (dt_emissao_nf + timedelta(days=config_cond["intervalo_dias"] * i)).date()
            comissao_parcela = round(valor_parcela_base * (comissao_final_pct / 100), 2)

            hoje = datetime.now().date()
            if dt_vencimento < hoje:
                st_parcela = random.choices(["PAGA", "INADIMPLENTE"], weights=[0.88, 0.12])[0]
            else:
                st_parcela = "EM_ABERTO"

            dt_recebimento_real = None
            comissao_liberada = False

            if st_parcela == "PAGA":
                dt_recebimento_real = datetime.combine(dt_vencimento, datetime.min.time()) + timedelta(hours=random.randint(9, 17))
                dt_recebimento_real = dt_recebimento_real.strftime("%Y-%m-%dT%H:%M:%S")
                comissao_liberada = True
                valor_comissao_liberada_caixa += comissao_parcela
                parcelas_pagas_count += 1
            elif st_parcela == "INADIMPLENTE":
                parcelas_inadimplentes_count += 1

            parcelas_cronograma.append({
                "numero_parcela": i,
                "total_parcelas": total_parc,
                "valor_parcela_brl": valor_parcela_base,
                "data_vencimento": dt_vencimento.strftime("%Y-%m-%d"),
                "status_parcela": st_parcela,
                "data_recebimento_real": dt_recebimento_real,
                "valor_comissao_parcela_brl": comissao_parcela,
                "comissao_liberada": comissao_liberada
            })

    # Status Global de Liquidação
    if status_venda != "FATURADO":
        status_global_recebimento = "AGUARDANDO_FATURAMENTO" if status_venda != "CANCELADO" else "CANCELADO"
    elif parcelas_pagas_count == total_parc:
        status_global_recebimento = "QUITADO"
    elif parcelas_inadimplentes_count > 0:
        status_global_recebimento = "INADIMPLENTE"
    elif parcelas_pagas_count > 0:
        status_global_recebimento = "PARCIALMENTE_RECEBIDO"
    else:
        status_global_recebimento = "EM_ABERTO"

    valor_comissao_a_realizar = round(valor_comissao_total - valor_comissao_liberada_caixa, 2)

    return {
        "venda_id": f"VND-{fake.uuid4()[:12].upper()}",
        "numero_pedido": f"PED-{dt_pedido.year}-{random.randint(10000, 99999)}",
        "vendedor": vendedor,
        "cliente": cliente,
        "produto": {
            "produto_id": produto["produto_id"],
            "nome_produto": produto["nome"],
            "categoria": produto["categoria"],
            "classificacao_rentabilidade": produto["classificacao_rentabilidade"],
            "custo_unitario_brl": produto["custo"],
            "preco_tabela_unitario_brl": produto["tabela"],
            "desconto_maximo_permitido_pct": produto["desc_max"]
        },
        "quantidade": quantidade,
        "valor_total_tabela_brl": valor_tabela,
        "desconto_aplicado_pct": desconto_pct,
        "valor_total_praticado_brl": valor_praticado,
        "canal_venda": random.choice(CANOES_VENDA),
        "status_venda": status_venda,
        "dados_faturamento": {
            "faturado": status_venda == "FATURADO",
            "numero_nota_fiscal": nf_numero,
            "chave_acesso_nfe": nf_chave,
            "data_emissao_nf": dt_emissao_nf.strftime("%Y-%m-%dT%H:%M:%S") if dt_emissao_nf else None,
            "condicao_pagamento": cond_chave,
            "qtd_parcelas": total_parc,
            "status_global_recebimento": status_global_recebimento,
            "parcelas_cronograma": parcelas_cronograma
        },
        "comissao_auditoria": {
            "classificacao_produto": produto["classificacao_rentabilidade"],
            "margem_bruta_realizada_pct": margem_realizada_pct,
            "percentual_comissao_base_produto": produto["comissao_base_pct"],
            "penalizacao_desconto_pct": penalizacao_desconto_pct,
            "percentual_comissao_final_aplicado": comissao_final_pct,
            "valor_comissao_total_venda_brl": valor_comissao_total,
            "valor_comissao_liberada_caixa_brl": round(valor_comissao_liberada_caixa, 2),
            "valor_comissao_a_realizar_brl": valor_comissao_a_realizar,
            "alerta_auditoria_desconto": alerta_desconto,
            "motivo_alerta_auditoria": motivo_alerta_desconto,
            "alerta_margem_critica": alerta_margem_critica,
            "motivo_alerta_margem": motivo_alerta_margem
        },
        "data_pedido": dt_pedido.strftime("%Y-%m-%dT%H:%M:%S")
    }