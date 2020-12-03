mkdir data/models
cd data/models

wget https://s3.amazonaws.com/models.huggingface.co/bert/bert-base-uncased.tar.gz
tar -xzf bert-base-uncased.tar.gz
mv bert_config.json config.json

wget https://s3.amazonaws.com/models.huggingface.co/bert/bert-base-uncased-vocab.txt
mv bert-base-uncased-vocab.txt vocab.txt

#### change the hf_models.py in dpr/models

def get_bert_tokenizer(pretrained_cfg_name: str, do_lower_case: bool = True):
    return BertTokenizer.from_pretrained('/home/YOUR_USERNAME/scratch/DPR/data/models/vocab.txt', do_lower_case=do_lower_case)


class HFBertEncoder(BertModel):
   def init_encoder(cls, cfg_name: str, projection_dim: int = 0, dropout: float = 0.1, **kwargs) -> BertModel:
        #cfg = BertConfig.from_pretrained(cfg_name if cfg_name else 'bert-base-uncased')
        cfg = BertConfig.from_pretrained('/home/YOUR_USER_NAME/scratch/DPR/data/models/')