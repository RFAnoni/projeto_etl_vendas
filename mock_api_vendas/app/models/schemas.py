from pydantic import BaseModel, Field
from typing import Optional, List

class VendedorSchema(BaseModel):
    vendedor_id: str = Field(..., example="VND-104")
    nome: str = Field(..., example="Carlos Eduardo")
    cargo: str = Field(..., example="Executivo Senior")
    regional: str = Field(..., example="SP_CAPITAL")

class ClienteSchema(BaseModel):
    cliente_id: str = Field(..., example="CLI-882")
    nome_razao_social: str = Field(..., example="Tech Solutions LTDA")
    segmento: str = Field(..., example="Enterprise")
    uf: str = Field(..., example="SP")

class ProdutoSchema(BaseModel):
    produto_id: str = Field(..., example="PRD-001")
    nome_produto: str = Field(..., example="Licença ERP Cloud Express")
    categoria: str = Field(..., example="Software")
    classificacao_rentabilidade: str = Field(..., example="CLASSE_A_ALTA_MARGEM")
    custo_unitario_brl: float = Field(..., example=80.00)
    preco_tabela_unitario_brl: float = Field(..., example=290.00)
    desconto_maximo_permitido_pct: float = Field(..., example=15.0)

class ParcelaSchema(BaseModel):
    numero_parcela: int = Field(..., example=1)
    total_parcelas: int = Field(..., example=3)
    valor_parcela_brl: float = Field(..., example=870.00)
    data_vencimento: str = Field(..., example="2026-08-25")
    status_parcela: str = Field(..., example="PAGA") # PAGA, EM_ABERTO, INADIMPLENTE, CANCELADA
    data_recebimento_real: Optional[str] = Field(None, example="2026-08-24T14:20:00")
    valor_comissao_parcela_brl: float = Field(..., example=30.45)
    comissao_liberada: bool = Field(..., example=True)

class FaturamentoSchema(BaseModel):
    faturado: bool = Field(..., example=True)
    numero_nota_fiscal: Optional[str] = Field(None, example="NF-2026-88912")
    chave_acesso_nfe: Optional[str] = Field(None, example="35260712345678000195550010000089211001234567")
    data_emissao_nf: Optional[str] = Field(None, example="2026-07-28T10:30:00")
    condicao_pagamento: str = Field(..., example="30/60/90_DIAS")
    qtd_parcelas: int = Field(..., example=3)
    status_global_recebimento: str = Field(..., example="PARCIALMENTE_RECEBIDO") # AGUARDANDO_FATURAMENTO, EM_ABERTO, PARCIALMENTE_RECEBIDO, QUITADO, INADIMPLENTE
    parcelas_cronograma: List[ParcelaSchema]

class AuditoriaComissaoSchema(BaseModel):
    classificacao_produto: str = Field(..., example="CLASSE_A_ALTA_MARGEM")
    margem_bruta_realizada_pct: float = Field(..., example=69.35)
    percentual_comissao_base_produto: float = Field(..., example=5.0)
    penalizacao_desconto_pct: float = Field(..., example=1.5)
    percentual_comissao_final_aplicado: float = Field(..., example=3.5)
    valor_comissao_total_venda_brl: float = Field(..., example=91.35)
    valor_comissao_liberada_caixa_brl: float = Field(..., example=30.45) # Liberado proporcional ao que entrou
    valor_comissao_a_realizar_brl: float = Field(..., example=60.90)     # O que entrará conforme pagamentos
    alerta_auditoria_desconto: bool = Field(..., example=False)
    motivo_alerta_auditoria: Optional[str] = Field(None, example=None)
    alerta_margem_critica: bool = Field(..., example=False)
    motivo_alerta_margem: Optional[str] = Field(None, example=None)

class VendaSchema(BaseModel):
    venda_id: str = Field(..., example="VND-99201")
    numero_pedido: str = Field(..., example="PED-2026-8812")
    vendedor: VendedorSchema
    cliente: ClienteSchema
    produto: ProdutoSchema
    quantidade: int = Field(..., example=10)
    valor_total_tabela_brl: float = Field(..., example=2900.00)
    desconto_aplicado_pct: float = Field(..., example=10.0)
    valor_total_praticado_brl: float = Field(..., example=2610.00)
    canal_venda: str = Field(..., example="B2B_DIRECT")
    status_venda: str = Field(..., example="FATURADO") # EM_APROVACAO, APROVADO, FATURADO, CANCELADO
    dados_faturamento: FaturamentoSchema
    comissao_auditoria: AuditoriaComissaoSchema
    data_pedido: str = Field(..., example="2026-07-25T14:30:00")