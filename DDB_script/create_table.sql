aws dynamodb create-table  --billing-mode PAY_PER_REQUEST --table-name PROGRAMME `
  --attribute-definitions `
  AttributeName=PROG_CODE,AttributeType=S `
  AttributeName=PROG_PROVIDER,AttributeType=S `
  AttributeName=FACULTY,AttributeType=S `
  AttributeName=AREA,AttributeType=S `
  AttributeName=DURATION,AttributeType=S `
  AttributeName=ENTRY_REQ_ENG,AttributeType=S `
  AttributeName=ENTRY_REQ_GENERAL,AttributeType=S `
  AttributeName=ENTRY_REQ_OTHER,AttributeType=S `
  AttributeName=MODE_OF_STUDY,AttributeType=S `
  AttributeName=PROG_DESC,AttributeType=S `
  AttributeName=PROG_NAME,AttributeType=S `
  AttributeName=IMG1,AttributeType=S `
  AttributeName=IMG2,AttributeType=S `
  AttributeName=Y1_TUITION_FEE,AttributeType=S `
  AttributeName=Y2_TUITION_FEE,AttributeType=S `
  AttributeName=Y3_TUITION_FEE,AttributeType=S `
  AttributeName=FEATURED,AttributeType=S  --key-schema `
  AttributeName=PROG_CODE,KeyType=HASH `
  AttributeName=PROG_PROVIDER,KeyType=RANGE




aws dynamodb create-table \
--table-name MusicCollection \
--attribute-definitions \
  AttributeName=Artist,AttributeType=S \
  AttributeName=SongTitle,AttributeType=S \
  AttributeName=AlbumTitle,AttributeType=S \
--key-schema \
  AttributeName=Artist,KeyType=HASH \
  AttributeName=SongTitle,KeyType=RANGE \
--provisioned-throughput \
  ReadCapacityUnits=10,WriteCapacityUnits=5
