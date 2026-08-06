from uuid import uuid4

def test_upload_dataset_success(client):
    """
    Testa o fluxo real de upload enviando bytes simulados 
    e verificando a resposta e persistência.
    """
    # Simulando um arquivo na memória
    file_content = b"Conteudo fake do documento corporativo."
    
    
    files = [
        ("files", ("relatorio_2026.pdf", file_content, "application/pdf")),
        ("files", ("planilha_vendas.csv", b"col1,col2\n1,2", "text/csv"))
    ]
    data = {"name": "Dataset Financeiro"}

    
    response = client.post("/datasets/", data=data, files=files)
    
    
    assert response.status_code == 201
    response_data = response.json()
    assert "id" in response_data
    assert response_data["name"] == "Dataset Financeiro"


def test_get_dataset_status_not_found(client):
    """
    Garante que a API retorna 404 limpo quando o dataset não existe.
    """
    fake_id = uuid4()
    
    response = client.get(f"/datasets/{fake_id}/status")
    
    assert response.status_code == 404
    assert "não encontrado" in response.json()["detail"].lower()