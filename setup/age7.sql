CREATE DATABASE IF NOT EXISTS age7;

CREATE TABLE IF NOT EXISTS age7.dm_unidade_orc
 (ID_UNIDADE_ORC BIGINT,
  SQA_UNIDADE_ORCAM BIGINT,
  ANO_EXERCICIO SMALLINT,
  CD_UNIDADE_ORC INT,
  ID_GRUPO_ADMINISTRACAO TINYINT,
  GRUPO_ADMINISTRACAO VARCHAR(100),
  ID_ADMINISTRACAO TINYINT,
  ADMINISTRACAO VARCHAR(100),
  NOME VARCHAR(100),
  SIGLA VARCHAR(30),
  PRIMARY KEY (ID_UNIDADE_ORC)
 );

CREATE TABLE IF NOT EXISTS age7.ft_receita_v2018
 (ID_TEMPO SMALLINT,
  ID_UNIDADE_ORC BIGINT,
  ID_ORIGEM INT,
  ID_ESPECIE INT,
  ID_DESDOBRAMENTO_1 INT,
  ID_DESDOBRAMENTO_2 INT,
  ID_DESDOBRAMENTO_3 INT,
  ID_TIPO INT,
  ID_ITEM INT,
  ID_SUBITEM INT,
  ID_FONTE INT,
  CD_FONTE TINYINT,
  CD_CLASSIFICACAO_REC BIGINT,
  ANO_PARTICAO SMALLINT,
  VR_EFETIVADO DECIMAL(15,2),
  FOREIGN KEY (ID_UNIDADE_ORC) REFERENCES dm_unidade_orc(ID_UNIDADE_ORC)
 );

CREATE TABLE IF NOT EXISTS age7.ft_convenio_entrada 
   (ID_TEMPO INT, 
	ID_ORGAO BIGINT, 
	ID_CONVENIO BIGINT, 
	ID_CONCEDENTE BIGINT, 
	ID_UNIDADE_ORC BIGINT, 
	ID_SITUACAO SMALLINT, 
	ANO_PARTICAO SMALLINT, 
	VR_CONCEDENTE_ATUAL DECIMAL(15,2), 
	VR_PROPONENTE_ATUAL DECIMAL(15,2),
   FOREIGN KEY (ID_UNIDADE_ORC) REFERENCES dm_unidade_orc(ID_UNIDADE_ORC)
   );

GRANT ALL ON *.* to root@'192.168.33.10' IDENTIFIED BY 'root'; 

FLUSH PRIVILEGES;