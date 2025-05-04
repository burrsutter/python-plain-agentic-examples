mc rm myminio/invoices/intake/$1
mc rm myminio/invoices/done/$1.done
mc rm myminio/invoices/error/$1.error
mc rm myminio/invoices/json/$1.json

mc ls myminio/invoices/intake/
mc ls myminio/invoices/done/
mc ls myminio/invoices/error/
mc ls myminio/invoices/json/