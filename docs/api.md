---
title: Click2Mail Document Submission API v1.0.0
language_tabs:
  - shell: Shell
  - http: HTTP
  - javascript: JavaScript
  - ruby: Ruby
  - python: Python
  - php: PHP
  - java: Java
  - go: Go
toc_footers: []
includes: []
search: true
highlight_theme: darkula
headingLevel: 2

---

<!-- Generator: Widdershins v4.0.1 -->

<h1 id="click2mail-document-submission-api">Click2Mail Document Submission API v1.0.0</h1>

> Scroll down for code samples, example requests and responses. Select a language for code samples from the tabs above or the mobile navigation menu.

API for submitting document jobs using the Click2Mail API Version 2

Base URLs:

* <a href="https://api.noname.com">https://api.noname.com</a>

License: <a href="https://opensource.org/licenses/NONE_YET">MIT</a>

# Authentication

- HTTP Authentication, scheme: bearer 

<h1 id="click2mail-document-submission-api-jobs">jobs</h1>

Operations related to jobs

## submitSingleDoc

<a id="opIdsubmitSingleDoc"></a>

> Code samples

```shell
# You can also use wget
curl -X POST https://api.noname.com/jobs/submit/single/doc \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -H 'Authorization: Bearer {access-token}'

```

```http
POST https://api.noname.com/jobs/submit/single/doc HTTP/1.1
Host: api.noname.com
Content-Type: application/json
Accept: application/json

```

```javascript
const inputBody = '{
  "documentSourceIdentifier": {
    "documentId": "string"
  },
  "recipientAddresses": [
    {
      "firstName": "string",
      "lastName": "string",
      "nickName": "string",
      "address1": "string",
      "address2": "string",
      "address3": "string",
      "city": "string",
      "state": "string",
      "zip": "string",
      "country": "string",
      "phoneNumber": "string"
    }
  ],
  "jobOptions": {
    "documentClass": "businessLetter",
    "layout": "portrait",
    "mailclass": "firstClassMail",
    "paperType": "letter",
    "printOption": "none",
    "envelope": "flat"
  },
  "paymentDetails": {
    "billingType": "creditCard",
    "creditCardDetails": {
      "cardType": "visa",
      "cardNumber": "string",
      "expirationDate": {
        "month": 1,
        "year": 2000
      },
      "cvv": 0
    },
    "invoiceDetails": {
      "invoiceNumber": "string",
      "amountDue": 0
    },
    "achDetails": {
      "routingNumber": "string",
      "accountNumber": "string",
      "checkDigit": 0
    },
    "creditAmount": {
      "amount": 0,
      "currency": "USD"
    }
  },
  "tags": [
    "string"
  ]
}';
const headers = {
  'Content-Type':'application/json',
  'Accept':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('https://api.noname.com/jobs/submit/single/doc',
{
  method: 'POST',
  body: inputBody,
  headers: headers
})
.then(function(res) {
    return res.json();
}).then(function(body) {
    console.log(body);
});

```

```ruby
require 'rest-client'
require 'json'

headers = {
  'Content-Type' => 'application/json',
  'Accept' => 'application/json',
  'Authorization' => 'Bearer {access-token}'
}

result = RestClient.post 'https://api.noname.com/jobs/submit/single/doc',
  params: {
  }, headers: headers

p JSON.parse(result)

```

```python
import requests
headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.post('https://api.noname.com/jobs/submit/single/doc', headers = headers)

print(r.json())

```

```php
<?php

require 'vendor/autoload.php';

$headers = array(
    'Content-Type' => 'application/json',
    'Accept' => 'application/json',
    'Authorization' => 'Bearer {access-token}',
);

$client = new \GuzzleHttp\Client();

// Define array of request body.
$request_body = array();

try {
    $response = $client->request('POST','https://api.noname.com/jobs/submit/single/doc', array(
        'headers' => $headers,
        'json' => $request_body,
       )
    );
    print_r($response->getBody()->getContents());
 }
 catch (\GuzzleHttp\Exception\BadResponseException $e) {
    // handle exception or api errors.
    print_r($e->getMessage());
 }

 // ...

```

```java
URL obj = new URL("https://api.noname.com/jobs/submit/single/doc");
HttpURLConnection con = (HttpURLConnection) obj.openConnection();
con.setRequestMethod("POST");
int responseCode = con.getResponseCode();
BufferedReader in = new BufferedReader(
    new InputStreamReader(con.getInputStream()));
String inputLine;
StringBuffer response = new StringBuffer();
while ((inputLine = in.readLine()) != null) {
    response.append(inputLine);
}
in.close();
System.out.println(response.toString());

```

```go
package main

import (
       "bytes"
       "net/http"
)

func main() {

    headers := map[string][]string{
        "Content-Type": []string{"application/json"},
        "Accept": []string{"application/json"},
        "Authorization": []string{"Bearer {access-token}"},
    }

    data := bytes.NewBuffer([]byte{jsonReq})
    req, err := http.NewRequest("POST", "https://api.noname.com/jobs/submit/single/doc", data)
    req.Header = headers

    client := &http.Client{}
    resp, err := client.Do(req)
    // ...
}

```

`POST /jobs/submit/single/doc`

*Submit a single document to multiple recipients*

Submit a single document to multiple recipients

> Body parameter

```json
{
  "documentSourceIdentifier": {
    "documentId": "string"
  },
  "recipientAddresses": [
    {
      "firstName": "string",
      "lastName": "string",
      "nickName": "string",
      "address1": "string",
      "address2": "string",
      "address3": "string",
      "city": "string",
      "state": "string",
      "zip": "string",
      "country": "string",
      "phoneNumber": "string"
    }
  ],
  "jobOptions": {
    "documentClass": "businessLetter",
    "layout": "portrait",
    "mailclass": "firstClassMail",
    "paperType": "letter",
    "printOption": "none",
    "envelope": "flat"
  },
  "paymentDetails": {
    "billingType": "creditCard",
    "creditCardDetails": {
      "cardType": "visa",
      "cardNumber": "string",
      "expirationDate": {
        "month": 1,
        "year": 2000
      },
      "cvv": 0
    },
    "invoiceDetails": {
      "invoiceNumber": "string",
      "amountDue": 0
    },
    "achDetails": {
      "routingNumber": "string",
      "accountNumber": "string",
      "checkDigit": 0
    },
    "creditAmount": {
      "amount": 0,
      "currency": "USD"
    }
  },
  "tags": [
    "string"
  ]
}
```

<h3 id="submitsingledoc-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|object|true|none|
|» documentSourceIdentifier|body|any|true|none|
|»» *anonymous*|body|object|false|none|
|»»» documentId|body|string|true|none|
|»» *anonymous*|body|object|false|none|
|»»» externalUrl|body|string(uri)|true|none|
|»» *anonymous*|body|object|false|none|
|»»» uploadRequestId|body|string|true|none|
|»»» documentName|body|string|true|none|
|»» *anonymous*|body|object|false|none|
|»»» uploadRequestId|body|string|true|none|
|»»» zipId|body|string|true|none|
|»»» documentName|body|string|true|none|
|»» *anonymous*|body|object|false|none|
|»»» zipId|body|string|true|none|
|»»» documentName|body|string|true|none|
|» recipientAddresses|body|[oneOf]|false|none|
|»» *anonymous*|body|[RecipientAddress](#schemarecipientaddress)|false|none|
|»»» firstName|body|string|true|none|
|»»» lastName|body|string|true|none|
|»»» nickName|body|string|false|none|
|»»» address1|body|string|true|none|
|»»» address2|body|string|false|none|
|»»» address3|body|string|false|none|
|»»» city|body|string|true|none|
|»»» state|body|string|true|none|
|»»» zip|body|string|true|none|
|»»» country|body|string|true|none|
|»»» phoneNumber|body|string|false|none|
|»» *anonymous*|body|object|false|none|
|»»» addressListId|body|string|true|none|
|»» *anonymous*|body|object|false|none|
|»»» addressId|body|string|true|none|
|» jobOptions|body|[JobOptions](#schemajoboptions)|true|none|
|»» documentClass|body|string|true|none|
|»» layout|body|string|true|none|
|»» mailclass|body|string|true|none|
|»» paperType|body|string|true|none|
|»» printOption|body|string|true|none|
|»» envelope|body|string|true|none|
|» paymentDetails|body|[PaymentDetails](#schemapaymentdetails)|false|none|
|»» billingType|body|string|true|none|
|»» creditCardDetails|body|[CreditCardDetails](#schemacreditcarddetails)|false|none|
|»»» cardType|body|string|true|none|
|»»» cardNumber|body|string|true|none|
|»»» expirationDate|body|object|true|none|
|»»»» month|body|integer|true|none|
|»»»» year|body|integer|true|none|
|»»» cvv|body|integer|true|none|
|»» invoiceDetails|body|object|false|none|
|»»» invoiceNumber|body|string|false|none|
|»»» amountDue|body|number|false|none|
|»» achDetails|body|[ACHDetails](#schemaachdetails)|false|none|
|»»» routingNumber|body|string|true|none|
|»»» accountNumber|body|string|true|none|
|»»» checkDigit|body|integer|true|none|
|»» creditAmount|body|[CreditAmount](#schemacreditamount)|false|none|
|»»» amount|body|number|true|none|
|»»» currency|body|string|true|none|
|» tags|body|[string]|false|none|

#### Enumerated Values

|Parameter|Value|
|---|---|
|»» documentClass|businessLetter|
|»» documentClass|personalLetter|
|»» layout|portrait|
|»» layout|landscape|
|»» mailclass|firstClassMail|
|»» mailclass|priorityMail|
|»» mailclass|largeEnvelope|
|»» paperType|letter|
|»» paperType|legal|
|»» paperType|postcard|
|»» printOption|none|
|»» printOption|color|
|»» printOption|grayscale|
|»» envelope|flat|
|»» envelope|windowedFlat|
|»» envelope|letter|
|»» envelope|legal|
|»» envelope|postcard|
|»» billingType|creditCard|
|»» billingType|invoice|
|»» billingType|ach|
|»» billingType|userCredit|
|»»» cardType|visa|
|»»» cardType|mastercard|
|»»» cardType|discover|
|»»» cardType|americanExpress|
|»»» currency|USD|
|»»» currency|EUR|
|»»» currency|GBP|
|»»» currency|CAD|
|»»» currency|AUD|

> Example responses

> 200 Response

```json
{
  "jobId": "string",
  "status": "string"
}
```

<h3 id="submitsingledoc-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Job submission accepted|Inline|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|Invalid request|None|
|401|[Unauthorized](https://tools.ietf.org/html/rfc7235#section-3.1)|Unauthorized|None|

<h3 id="submitsingledoc-responseschema">Response Schema</h3>

Status Code **200**

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» jobId|string|false|none|none|
|» status|string|false|none|none|

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
bearerAuth
</aside>

## post_jobs_submit_multi_doc

<a id="opIdpost_jobs_submit_multi_doc"></a>

> Code samples

```shell
# You can also use wget
curl -X POST https://api.noname.com/jobs/submit/multi/doc \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer {access-token}'

```

```http
POST https://api.noname.com/jobs/submit/multi/doc HTTP/1.1
Host: api.noname.com
Content-Type: application/json

```

```javascript
const inputBody = '{
  "documentRecipientPairs": [
    {
      "documentSourceIdentifier": {
        "documentId": "string"
      },
      "recipientAddressSource": {
        "firstName": "string",
        "lastName": "string",
        "nickName": "string",
        "address1": "string",
        "address2": "string",
        "address3": "string",
        "city": "string",
        "state": "string",
        "zip": "string",
        "country": "string",
        "phoneNumber": "string"
      }
    }
  ],
  "jobOptions": {
    "documentClass": "businessLetter",
    "layout": "portrait",
    "mailclass": "firstClassMail",
    "paperType": "letter",
    "printOption": "none",
    "envelope": "flat"
  },
  "paymentDetails": {
    "billingType": "creditCard",
    "creditCardDetails": {
      "cardType": "visa",
      "cardNumber": "string",
      "expirationDate": {
        "month": 1,
        "year": 2000
      },
      "cvv": 0
    },
    "invoiceDetails": {
      "invoiceNumber": "string",
      "amountDue": 0
    },
    "achDetails": {
      "routingNumber": "string",
      "accountNumber": "string",
      "checkDigit": 0
    },
    "creditAmount": {
      "amount": 0,
      "currency": "USD"
    }
  },
  "tags": [
    "string"
  ]
}';
const headers = {
  'Content-Type':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('https://api.noname.com/jobs/submit/multi/doc',
{
  method: 'POST',
  body: inputBody,
  headers: headers
})
.then(function(res) {
    return res.json();
}).then(function(body) {
    console.log(body);
});

```

```ruby
require 'rest-client'
require 'json'

headers = {
  'Content-Type' => 'application/json',
  'Authorization' => 'Bearer {access-token}'
}

result = RestClient.post 'https://api.noname.com/jobs/submit/multi/doc',
  params: {
  }, headers: headers

p JSON.parse(result)

```

```python
import requests
headers = {
  'Content-Type': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.post('https://api.noname.com/jobs/submit/multi/doc', headers = headers)

print(r.json())

```

```php
<?php

require 'vendor/autoload.php';

$headers = array(
    'Content-Type' => 'application/json',
    'Authorization' => 'Bearer {access-token}',
);

$client = new \GuzzleHttp\Client();

// Define array of request body.
$request_body = array();

try {
    $response = $client->request('POST','https://api.noname.com/jobs/submit/multi/doc', array(
        'headers' => $headers,
        'json' => $request_body,
       )
    );
    print_r($response->getBody()->getContents());
 }
 catch (\GuzzleHttp\Exception\BadResponseException $e) {
    // handle exception or api errors.
    print_r($e->getMessage());
 }

 // ...

```

```java
URL obj = new URL("https://api.noname.com/jobs/submit/multi/doc");
HttpURLConnection con = (HttpURLConnection) obj.openConnection();
con.setRequestMethod("POST");
int responseCode = con.getResponseCode();
BufferedReader in = new BufferedReader(
    new InputStreamReader(con.getInputStream()));
String inputLine;
StringBuffer response = new StringBuffer();
while ((inputLine = in.readLine()) != null) {
    response.append(inputLine);
}
in.close();
System.out.println(response.toString());

```

```go
package main

import (
       "bytes"
       "net/http"
)

func main() {

    headers := map[string][]string{
        "Content-Type": []string{"application/json"},
        "Authorization": []string{"Bearer {access-token}"},
    }

    data := bytes.NewBuffer([]byte{jsonReq})
    req, err := http.NewRequest("POST", "https://api.noname.com/jobs/submit/multi/doc", data)
    req.Header = headers

    client := &http.Client{}
    resp, err := client.Do(req)
    // ...
}

```

`POST /jobs/submit/multi/doc`

*Submit multiple documents, each to a different recipient*

Submit multiple documents, each to a different recipient

> Body parameter

```json
{
  "documentRecipientPairs": [
    {
      "documentSourceIdentifier": {
        "documentId": "string"
      },
      "recipientAddressSource": {
        "firstName": "string",
        "lastName": "string",
        "nickName": "string",
        "address1": "string",
        "address2": "string",
        "address3": "string",
        "city": "string",
        "state": "string",
        "zip": "string",
        "country": "string",
        "phoneNumber": "string"
      }
    }
  ],
  "jobOptions": {
    "documentClass": "businessLetter",
    "layout": "portrait",
    "mailclass": "firstClassMail",
    "paperType": "letter",
    "printOption": "none",
    "envelope": "flat"
  },
  "paymentDetails": {
    "billingType": "creditCard",
    "creditCardDetails": {
      "cardType": "visa",
      "cardNumber": "string",
      "expirationDate": {
        "month": 1,
        "year": 2000
      },
      "cvv": 0
    },
    "invoiceDetails": {
      "invoiceNumber": "string",
      "amountDue": 0
    },
    "achDetails": {
      "routingNumber": "string",
      "accountNumber": "string",
      "checkDigit": 0
    },
    "creditAmount": {
      "amount": 0,
      "currency": "USD"
    }
  },
  "tags": [
    "string"
  ]
}
```

<h3 id="post_jobs_submit_multi_doc-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|object|true|none|
|» documentRecipientPairs|body|[object]|true|none|
|»» documentSourceIdentifier|body|any|true|none|
|»»» *anonymous*|body|object|false|none|
|»»»» documentId|body|string|true|none|
|»»» *anonymous*|body|object|false|none|
|»»»» externalUrl|body|string(uri)|true|none|
|»»» *anonymous*|body|object|false|none|
|»»»» uploadRequestId|body|string|true|none|
|»»»» documentName|body|string|true|none|
|»»» *anonymous*|body|object|false|none|
|»»»» uploadRequestId|body|string|true|none|
|»»»» zipId|body|string|true|none|
|»»»» documentName|body|string|true|none|
|»»» *anonymous*|body|object|false|none|
|»»»» zipId|body|string|true|none|
|»»»» documentName|body|string|true|none|
|»» recipientAddressSource|body|any|true|none|
|»»» *anonymous*|body|[RecipientAddress](#schemarecipientaddress)|false|none|
|»»»» firstName|body|string|true|none|
|»»»» lastName|body|string|true|none|
|»»»» nickName|body|string|false|none|
|»»»» address1|body|string|true|none|
|»»»» address2|body|string|false|none|
|»»»» address3|body|string|false|none|
|»»»» city|body|string|true|none|
|»»»» state|body|string|true|none|
|»»»» zip|body|string|true|none|
|»»»» country|body|string|true|none|
|»»»» phoneNumber|body|string|false|none|
|»»» *anonymous*|body|object|false|none|
|»»»» addressListId|body|string|true|none|
|»»» *anonymous*|body|object|false|none|
|»»»» addressId|body|string|true|none|
|» jobOptions|body|[JobOptions](#schemajoboptions)|true|none|
|»» documentClass|body|string|true|none|
|»» layout|body|string|true|none|
|»» mailclass|body|string|true|none|
|»» paperType|body|string|true|none|
|»» printOption|body|string|true|none|
|»» envelope|body|string|true|none|
|» paymentDetails|body|[PaymentDetails](#schemapaymentdetails)|false|none|
|»» billingType|body|string|true|none|
|»» creditCardDetails|body|[CreditCardDetails](#schemacreditcarddetails)|false|none|
|»»» cardType|body|string|true|none|
|»»» cardNumber|body|string|true|none|
|»»» expirationDate|body|object|true|none|
|»»»» month|body|integer|true|none|
|»»»» year|body|integer|true|none|
|»»» cvv|body|integer|true|none|
|»» invoiceDetails|body|object|false|none|
|»»» invoiceNumber|body|string|false|none|
|»»» amountDue|body|number|false|none|
|»» achDetails|body|[ACHDetails](#schemaachdetails)|false|none|
|»»» routingNumber|body|string|true|none|
|»»» accountNumber|body|string|true|none|
|»»» checkDigit|body|integer|true|none|
|»» creditAmount|body|[CreditAmount](#schemacreditamount)|false|none|
|»»» amount|body|number|true|none|
|»»» currency|body|string|true|none|
|» tags|body|[string]|false|none|

#### Enumerated Values

|Parameter|Value|
|---|---|
|»» documentClass|businessLetter|
|»» documentClass|personalLetter|
|»» layout|portrait|
|»» layout|landscape|
|»» mailclass|firstClassMail|
|»» mailclass|priorityMail|
|»» mailclass|largeEnvelope|
|»» paperType|letter|
|»» paperType|legal|
|»» paperType|postcard|
|»» printOption|none|
|»» printOption|color|
|»» printOption|grayscale|
|»» envelope|flat|
|»» envelope|windowedFlat|
|»» envelope|letter|
|»» envelope|legal|
|»» envelope|postcard|
|»» billingType|creditCard|
|»» billingType|invoice|
|»» billingType|ach|
|»» billingType|userCredit|
|»»» cardType|visa|
|»»» cardType|mastercard|
|»»» cardType|discover|
|»»» cardType|americanExpress|
|»»» currency|USD|
|»»» currency|EUR|
|»»» currency|GBP|
|»»» currency|CAD|
|»»» currency|AUD|

<h3 id="post_jobs_submit_multi_doc-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|OK|None|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|Invalid request|None|
|401|[Unauthorized](https://tools.ietf.org/html/rfc7235#section-3.1)|Unauthorized|None|

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
bearerAuth
</aside>

## post_jobs_submit_multi_doc_merge

<a id="opIdpost_jobs_submit_multi_doc_merge"></a>

> Code samples

```shell
# You can also use wget
curl -X POST https://api.noname.com/jobs/submit/multi/doc/merge \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer {access-token}'

```

```http
POST https://api.noname.com/jobs/submit/multi/doc/merge HTTP/1.1
Host: api.noname.com
Content-Type: application/json

```

```javascript
const inputBody = '{
  "documentsToMerge": [
    {
      "documentId": "string"
    }
  ],
  "recipientAddressSource": {
    "firstName": "string",
    "lastName": "string",
    "nickName": "string",
    "address1": "string",
    "address2": "string",
    "address3": "string",
    "city": "string",
    "state": "string",
    "zip": "string",
    "country": "string",
    "phoneNumber": "string"
  },
  "tags": [
    "string"
  ]
}';
const headers = {
  'Content-Type':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('https://api.noname.com/jobs/submit/multi/doc/merge',
{
  method: 'POST',
  body: inputBody,
  headers: headers
})
.then(function(res) {
    return res.json();
}).then(function(body) {
    console.log(body);
});

```

```ruby
require 'rest-client'
require 'json'

headers = {
  'Content-Type' => 'application/json',
  'Authorization' => 'Bearer {access-token}'
}

result = RestClient.post 'https://api.noname.com/jobs/submit/multi/doc/merge',
  params: {
  }, headers: headers

p JSON.parse(result)

```

```python
import requests
headers = {
  'Content-Type': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.post('https://api.noname.com/jobs/submit/multi/doc/merge', headers = headers)

print(r.json())

```

```php
<?php

require 'vendor/autoload.php';

$headers = array(
    'Content-Type' => 'application/json',
    'Authorization' => 'Bearer {access-token}',
);

$client = new \GuzzleHttp\Client();

// Define array of request body.
$request_body = array();

try {
    $response = $client->request('POST','https://api.noname.com/jobs/submit/multi/doc/merge', array(
        'headers' => $headers,
        'json' => $request_body,
       )
    );
    print_r($response->getBody()->getContents());
 }
 catch (\GuzzleHttp\Exception\BadResponseException $e) {
    // handle exception or api errors.
    print_r($e->getMessage());
 }

 // ...

```

```java
URL obj = new URL("https://api.noname.com/jobs/submit/multi/doc/merge");
HttpURLConnection con = (HttpURLConnection) obj.openConnection();
con.setRequestMethod("POST");
int responseCode = con.getResponseCode();
BufferedReader in = new BufferedReader(
    new InputStreamReader(con.getInputStream()));
String inputLine;
StringBuffer response = new StringBuffer();
while ((inputLine = in.readLine()) != null) {
    response.append(inputLine);
}
in.close();
System.out.println(response.toString());

```

```go
package main

import (
       "bytes"
       "net/http"
)

func main() {

    headers := map[string][]string{
        "Content-Type": []string{"application/json"},
        "Authorization": []string{"Bearer {access-token}"},
    }

    data := bytes.NewBuffer([]byte{jsonReq})
    req, err := http.NewRequest("POST", "https://api.noname.com/jobs/submit/multi/doc/merge", data)
    req.Header = headers

    client := &http.Client{}
    resp, err := client.Do(req)
    // ...
}

```

`POST /jobs/submit/multi/doc/merge`

*Merge multiple documents and send to a single recipient*

Merge multiple documents and send to a single recipient

> Body parameter

```json
{
  "documentsToMerge": [
    {
      "documentId": "string"
    }
  ],
  "recipientAddressSource": {
    "firstName": "string",
    "lastName": "string",
    "nickName": "string",
    "address1": "string",
    "address2": "string",
    "address3": "string",
    "city": "string",
    "state": "string",
    "zip": "string",
    "country": "string",
    "phoneNumber": "string"
  },
  "tags": [
    "string"
  ]
}
```

<h3 id="post_jobs_submit_multi_doc_merge-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|object|true|none|
|» documentsToMerge|body|[oneOf]|true|none|
|»» *anonymous*|body|object|false|none|
|»»» documentId|body|string|true|none|
|»» *anonymous*|body|object|false|none|
|»»» externalUrl|body|string(uri)|true|none|
|»» *anonymous*|body|object|false|none|
|»»» uploadRequestId|body|string|true|none|
|»»» documentName|body|string|true|none|
|»» *anonymous*|body|object|false|none|
|»»» uploadRequestId|body|string|true|none|
|»»» zipId|body|string|true|none|
|»»» documentName|body|string|true|none|
|»» *anonymous*|body|object|false|none|
|»»» zipId|body|string|true|none|
|»»» documentName|body|string|true|none|
|» recipientAddressSource|body|any|true|none|
|»» *anonymous*|body|[RecipientAddress](#schemarecipientaddress)|false|none|
|»»» firstName|body|string|true|none|
|»»» lastName|body|string|true|none|
|»»» nickName|body|string|false|none|
|»»» address1|body|string|true|none|
|»»» address2|body|string|false|none|
|»»» address3|body|string|false|none|
|»»» city|body|string|true|none|
|»»» state|body|string|true|none|
|»»» zip|body|string|true|none|
|»»» country|body|string|true|none|
|»»» phoneNumber|body|string|false|none|
|»» *anonymous*|body|object|false|none|
|»»» addressListId|body|string|true|none|
|»» *anonymous*|body|object|false|none|
|»»» addressId|body|string|true|none|
|» tags|body|[string]|false|none|

<h3 id="post_jobs_submit_multi_doc_merge-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|OK|None|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|Invalid request|None|
|401|[Unauthorized](https://tools.ietf.org/html/rfc7235#section-3.1)|Unauthorized|None|

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
bearerAuth
</aside>

## post_jobs_submit_single_doc_jobTemplate

<a id="opIdpost_jobs_submit_single_doc_jobTemplate"></a>

> Code samples

```shell
# You can also use wget
curl -X POST https://api.noname.com/jobs/submit/single/doc/jobTemplate \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer {access-token}'

```

```http
POST https://api.noname.com/jobs/submit/single/doc/jobTemplate HTTP/1.1
Host: api.noname.com
Content-Type: application/json

```

```javascript
const inputBody = '{
  "documentSourceIdentifier": {
    "documentId": "string"
  },
  "recipientAddresses": [
    {
      "firstName": "string",
      "lastName": "string",
      "nickName": "string",
      "address1": "string",
      "address2": "string",
      "address3": "string",
      "city": "string",
      "state": "string",
      "zip": "string",
      "country": "string",
      "phoneNumber": "string"
    }
  ],
  "jobTemplate": "string",
  "jobOptions": {
    "documentClass": "businessLetter",
    "layout": "portrait",
    "mailclass": "firstClassMail",
    "paperType": "letter",
    "printOption": "none",
    "envelope": "flat"
  },
  "paymentDetails": {
    "billingType": "creditCard",
    "creditCardDetails": {
      "cardType": "visa",
      "cardNumber": "string",
      "expirationDate": {
        "month": 1,
        "year": 2000
      },
      "cvv": 0
    },
    "invoiceDetails": {
      "invoiceNumber": "string",
      "amountDue": 0
    },
    "achDetails": {
      "routingNumber": "string",
      "accountNumber": "string",
      "checkDigit": 0
    },
    "creditAmount": {
      "amount": 0,
      "currency": "USD"
    }
  },
  "tags": [
    "string"
  ]
}';
const headers = {
  'Content-Type':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('https://api.noname.com/jobs/submit/single/doc/jobTemplate',
{
  method: 'POST',
  body: inputBody,
  headers: headers
})
.then(function(res) {
    return res.json();
}).then(function(body) {
    console.log(body);
});

```

```ruby
require 'rest-client'
require 'json'

headers = {
  'Content-Type' => 'application/json',
  'Authorization' => 'Bearer {access-token}'
}

result = RestClient.post 'https://api.noname.com/jobs/submit/single/doc/jobTemplate',
  params: {
  }, headers: headers

p JSON.parse(result)

```

```python
import requests
headers = {
  'Content-Type': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.post('https://api.noname.com/jobs/submit/single/doc/jobTemplate', headers = headers)

print(r.json())

```

```php
<?php

require 'vendor/autoload.php';

$headers = array(
    'Content-Type' => 'application/json',
    'Authorization' => 'Bearer {access-token}',
);

$client = new \GuzzleHttp\Client();

// Define array of request body.
$request_body = array();

try {
    $response = $client->request('POST','https://api.noname.com/jobs/submit/single/doc/jobTemplate', array(
        'headers' => $headers,
        'json' => $request_body,
       )
    );
    print_r($response->getBody()->getContents());
 }
 catch (\GuzzleHttp\Exception\BadResponseException $e) {
    // handle exception or api errors.
    print_r($e->getMessage());
 }

 // ...

```

```java
URL obj = new URL("https://api.noname.com/jobs/submit/single/doc/jobTemplate");
HttpURLConnection con = (HttpURLConnection) obj.openConnection();
con.setRequestMethod("POST");
int responseCode = con.getResponseCode();
BufferedReader in = new BufferedReader(
    new InputStreamReader(con.getInputStream()));
String inputLine;
StringBuffer response = new StringBuffer();
while ((inputLine = in.readLine()) != null) {
    response.append(inputLine);
}
in.close();
System.out.println(response.toString());

```

```go
package main

import (
       "bytes"
       "net/http"
)

func main() {

    headers := map[string][]string{
        "Content-Type": []string{"application/json"},
        "Authorization": []string{"Bearer {access-token}"},
    }

    data := bytes.NewBuffer([]byte{jsonReq})
    req, err := http.NewRequest("POST", "https://api.noname.com/jobs/submit/single/doc/jobTemplate", data)
    req.Header = headers

    client := &http.Client{}
    resp, err := client.Do(req)
    // ...
}

```

`POST /jobs/submit/single/doc/jobTemplate`

*Submit a document using a job template*

Submit a document using a job template

> Body parameter

```json
{
  "documentSourceIdentifier": {
    "documentId": "string"
  },
  "recipientAddresses": [
    {
      "firstName": "string",
      "lastName": "string",
      "nickName": "string",
      "address1": "string",
      "address2": "string",
      "address3": "string",
      "city": "string",
      "state": "string",
      "zip": "string",
      "country": "string",
      "phoneNumber": "string"
    }
  ],
  "jobTemplate": "string",
  "jobOptions": {
    "documentClass": "businessLetter",
    "layout": "portrait",
    "mailclass": "firstClassMail",
    "paperType": "letter",
    "printOption": "none",
    "envelope": "flat"
  },
  "paymentDetails": {
    "billingType": "creditCard",
    "creditCardDetails": {
      "cardType": "visa",
      "cardNumber": "string",
      "expirationDate": {
        "month": 1,
        "year": 2000
      },
      "cvv": 0
    },
    "invoiceDetails": {
      "invoiceNumber": "string",
      "amountDue": 0
    },
    "achDetails": {
      "routingNumber": "string",
      "accountNumber": "string",
      "checkDigit": 0
    },
    "creditAmount": {
      "amount": 0,
      "currency": "USD"
    }
  },
  "tags": [
    "string"
  ]
}
```

<h3 id="post_jobs_submit_single_doc_jobtemplate-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|object|true|none|
|» documentSourceIdentifier|body|any|true|none|
|»» *anonymous*|body|object|false|none|
|»»» documentId|body|string|true|none|
|»» *anonymous*|body|object|false|none|
|»»» externalUrl|body|string(uri)|true|none|
|»» *anonymous*|body|object|false|none|
|»»» uploadRequestId|body|string|true|none|
|»»» documentName|body|string|true|none|
|»» *anonymous*|body|object|false|none|
|»»» uploadRequestId|body|string|true|none|
|»»» zipId|body|string|true|none|
|»»» documentName|body|string|true|none|
|»» *anonymous*|body|object|false|none|
|»»» zipId|body|string|true|none|
|»»» documentName|body|string|true|none|
|» recipientAddresses|body|[oneOf]|false|none|
|»» *anonymous*|body|[RecipientAddress](#schemarecipientaddress)|false|none|
|»»» firstName|body|string|true|none|
|»»» lastName|body|string|true|none|
|»»» nickName|body|string|false|none|
|»»» address1|body|string|true|none|
|»»» address2|body|string|false|none|
|»»» address3|body|string|false|none|
|»»» city|body|string|true|none|
|»»» state|body|string|true|none|
|»»» zip|body|string|true|none|
|»»» country|body|string|true|none|
|»»» phoneNumber|body|string|false|none|
|»» *anonymous*|body|object|false|none|
|»»» addressListId|body|string|true|none|
|»» *anonymous*|body|object|false|none|
|»»» addressId|body|string|true|none|
|» jobTemplate|body|string|true|none|
|» jobOptions|body|[JobOptions](#schemajoboptions)|false|none|
|»» documentClass|body|string|true|none|
|»» layout|body|string|true|none|
|»» mailclass|body|string|true|none|
|»» paperType|body|string|true|none|
|»» printOption|body|string|true|none|
|»» envelope|body|string|true|none|
|» paymentDetails|body|[PaymentDetails](#schemapaymentdetails)|false|none|
|»» billingType|body|string|true|none|
|»» creditCardDetails|body|[CreditCardDetails](#schemacreditcarddetails)|false|none|
|»»» cardType|body|string|true|none|
|»»» cardNumber|body|string|true|none|
|»»» expirationDate|body|object|true|none|
|»»»» month|body|integer|true|none|
|»»»» year|body|integer|true|none|
|»»» cvv|body|integer|true|none|
|»» invoiceDetails|body|object|false|none|
|»»» invoiceNumber|body|string|false|none|
|»»» amountDue|body|number|false|none|
|»» achDetails|body|[ACHDetails](#schemaachdetails)|false|none|
|»»» routingNumber|body|string|true|none|
|»»» accountNumber|body|string|true|none|
|»»» checkDigit|body|integer|true|none|
|»» creditAmount|body|[CreditAmount](#schemacreditamount)|false|none|
|»»» amount|body|number|true|none|
|»»» currency|body|string|true|none|
|» tags|body|[string]|false|none|

#### Enumerated Values

|Parameter|Value|
|---|---|
|»» documentClass|businessLetter|
|»» documentClass|personalLetter|
|»» layout|portrait|
|»» layout|landscape|
|»» mailclass|firstClassMail|
|»» mailclass|priorityMail|
|»» mailclass|largeEnvelope|
|»» paperType|letter|
|»» paperType|legal|
|»» paperType|postcard|
|»» printOption|none|
|»» printOption|color|
|»» printOption|grayscale|
|»» envelope|flat|
|»» envelope|windowedFlat|
|»» envelope|letter|
|»» envelope|legal|
|»» envelope|postcard|
|»» billingType|creditCard|
|»» billingType|invoice|
|»» billingType|ach|
|»» billingType|userCredit|
|»»» cardType|visa|
|»»» cardType|mastercard|
|»»» cardType|discover|
|»»» cardType|americanExpress|
|»»» currency|USD|
|»»» currency|EUR|
|»»» currency|GBP|
|»»» currency|CAD|
|»»» currency|AUD|

<h3 id="post_jobs_submit_single_doc_jobtemplate-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|OK|None|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|Invalid request|None|
|401|[Unauthorized](https://tools.ietf.org/html/rfc7235#section-3.1)|Unauthorized|None|

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
bearerAuth
</aside>

## post_jobs_submit_multi_docs_jobtemplate

<a id="opIdpost_jobs_submit_multi_docs_jobtemplate"></a>

> Code samples

```shell
# You can also use wget
curl -X POST https://api.noname.com/jobs/submit/multi/docs/jobtemplate \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer {access-token}'

```

```http
POST https://api.noname.com/jobs/submit/multi/docs/jobtemplate HTTP/1.1
Host: api.noname.com
Content-Type: application/json

```

```javascript
const inputBody = '{
  "documentRecipientPairs": [
    {
      "documentSourceIdentifier": {
        "documentId": "string"
      },
      "recipientAddressSource": {
        "firstName": "string",
        "lastName": "string",
        "nickName": "string",
        "address1": "string",
        "address2": "string",
        "address3": "string",
        "city": "string",
        "state": "string",
        "zip": "string",
        "country": "string",
        "phoneNumber": "string"
      }
    }
  ],
  "jobTemplate": "string",
  "paymentDetails": {
    "billingType": "creditCard",
    "creditCardDetails": {
      "cardType": "visa",
      "cardNumber": "string",
      "expirationDate": {
        "month": 1,
        "year": 2000
      },
      "cvv": 0
    },
    "invoiceDetails": {
      "invoiceNumber": "string",
      "amountDue": 0
    },
    "achDetails": {
      "routingNumber": "string",
      "accountNumber": "string",
      "checkDigit": 0
    },
    "creditAmount": {
      "amount": 0,
      "currency": "USD"
    }
  },
  "tags": [
    "string"
  ]
}';
const headers = {
  'Content-Type':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('https://api.noname.com/jobs/submit/multi/docs/jobtemplate',
{
  method: 'POST',
  body: inputBody,
  headers: headers
})
.then(function(res) {
    return res.json();
}).then(function(body) {
    console.log(body);
});

```

```ruby
require 'rest-client'
require 'json'

headers = {
  'Content-Type' => 'application/json',
  'Authorization' => 'Bearer {access-token}'
}

result = RestClient.post 'https://api.noname.com/jobs/submit/multi/docs/jobtemplate',
  params: {
  }, headers: headers

p JSON.parse(result)

```

```python
import requests
headers = {
  'Content-Type': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.post('https://api.noname.com/jobs/submit/multi/docs/jobtemplate', headers = headers)

print(r.json())

```

```php
<?php

require 'vendor/autoload.php';

$headers = array(
    'Content-Type' => 'application/json',
    'Authorization' => 'Bearer {access-token}',
);

$client = new \GuzzleHttp\Client();

// Define array of request body.
$request_body = array();

try {
    $response = $client->request('POST','https://api.noname.com/jobs/submit/multi/docs/jobtemplate', array(
        'headers' => $headers,
        'json' => $request_body,
       )
    );
    print_r($response->getBody()->getContents());
 }
 catch (\GuzzleHttp\Exception\BadResponseException $e) {
    // handle exception or api errors.
    print_r($e->getMessage());
 }

 // ...

```

```java
URL obj = new URL("https://api.noname.com/jobs/submit/multi/docs/jobtemplate");
HttpURLConnection con = (HttpURLConnection) obj.openConnection();
con.setRequestMethod("POST");
int responseCode = con.getResponseCode();
BufferedReader in = new BufferedReader(
    new InputStreamReader(con.getInputStream()));
String inputLine;
StringBuffer response = new StringBuffer();
while ((inputLine = in.readLine()) != null) {
    response.append(inputLine);
}
in.close();
System.out.println(response.toString());

```

```go
package main

import (
       "bytes"
       "net/http"
)

func main() {

    headers := map[string][]string{
        "Content-Type": []string{"application/json"},
        "Authorization": []string{"Bearer {access-token}"},
    }

    data := bytes.NewBuffer([]byte{jsonReq})
    req, err := http.NewRequest("POST", "https://api.noname.com/jobs/submit/multi/docs/jobtemplate", data)
    req.Header = headers

    client := &http.Client{}
    resp, err := client.Do(req)
    // ...
}

```

`POST /jobs/submit/multi/docs/jobtemplate`

*Submit multiple documents with recipient addresses and job template*

Submit multiple documents with recipient addresses and job template

> Body parameter

```json
{
  "documentRecipientPairs": [
    {
      "documentSourceIdentifier": {
        "documentId": "string"
      },
      "recipientAddressSource": {
        "firstName": "string",
        "lastName": "string",
        "nickName": "string",
        "address1": "string",
        "address2": "string",
        "address3": "string",
        "city": "string",
        "state": "string",
        "zip": "string",
        "country": "string",
        "phoneNumber": "string"
      }
    }
  ],
  "jobTemplate": "string",
  "paymentDetails": {
    "billingType": "creditCard",
    "creditCardDetails": {
      "cardType": "visa",
      "cardNumber": "string",
      "expirationDate": {
        "month": 1,
        "year": 2000
      },
      "cvv": 0
    },
    "invoiceDetails": {
      "invoiceNumber": "string",
      "amountDue": 0
    },
    "achDetails": {
      "routingNumber": "string",
      "accountNumber": "string",
      "checkDigit": 0
    },
    "creditAmount": {
      "amount": 0,
      "currency": "USD"
    }
  },
  "tags": [
    "string"
  ]
}
```

<h3 id="post_jobs_submit_multi_docs_jobtemplate-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|object|true|none|
|» documentRecipientPairs|body|[object]|true|none|
|»» documentSourceIdentifier|body|any|true|none|
|»»» *anonymous*|body|object|false|none|
|»»»» documentId|body|string|true|none|
|»»» *anonymous*|body|object|false|none|
|»»»» externalUrl|body|string(uri)|true|none|
|»»» *anonymous*|body|object|false|none|
|»»»» uploadRequestId|body|string|true|none|
|»»»» documentName|body|string|true|none|
|»»» *anonymous*|body|object|false|none|
|»»»» uploadRequestId|body|string|true|none|
|»»»» zipId|body|string|true|none|
|»»»» documentName|body|string|true|none|
|»»» *anonymous*|body|object|false|none|
|»»»» zipId|body|string|true|none|
|»»»» documentName|body|string|true|none|
|»» recipientAddressSource|body|any|true|none|
|»»» *anonymous*|body|[RecipientAddress](#schemarecipientaddress)|false|none|
|»»»» firstName|body|string|true|none|
|»»»» lastName|body|string|true|none|
|»»»» nickName|body|string|false|none|
|»»»» address1|body|string|true|none|
|»»»» address2|body|string|false|none|
|»»»» address3|body|string|false|none|
|»»»» city|body|string|true|none|
|»»»» state|body|string|true|none|
|»»»» zip|body|string|true|none|
|»»»» country|body|string|true|none|
|»»»» phoneNumber|body|string|false|none|
|»»» *anonymous*|body|object|false|none|
|»»»» addressListId|body|string|true|none|
|»»» *anonymous*|body|object|false|none|
|»»»» addressId|body|string|true|none|
|» jobTemplate|body|string|true|none|
|» paymentDetails|body|[PaymentDetails](#schemapaymentdetails)|true|none|
|»» billingType|body|string|true|none|
|»» creditCardDetails|body|[CreditCardDetails](#schemacreditcarddetails)|false|none|
|»»» cardType|body|string|true|none|
|»»» cardNumber|body|string|true|none|
|»»» expirationDate|body|object|true|none|
|»»»» month|body|integer|true|none|
|»»»» year|body|integer|true|none|
|»»» cvv|body|integer|true|none|
|»» invoiceDetails|body|object|false|none|
|»»» invoiceNumber|body|string|false|none|
|»»» amountDue|body|number|false|none|
|»» achDetails|body|[ACHDetails](#schemaachdetails)|false|none|
|»»» routingNumber|body|string|true|none|
|»»» accountNumber|body|string|true|none|
|»»» checkDigit|body|integer|true|none|
|»» creditAmount|body|[CreditAmount](#schemacreditamount)|false|none|
|»»» amount|body|number|true|none|
|»»» currency|body|string|true|none|
|» tags|body|[string]|false|none|

#### Enumerated Values

|Parameter|Value|
|---|---|
|»» billingType|creditCard|
|»» billingType|invoice|
|»» billingType|ach|
|»» billingType|userCredit|
|»»» cardType|visa|
|»»» cardType|mastercard|
|»»» cardType|discover|
|»»» cardType|americanExpress|
|»»» currency|USD|
|»»» currency|EUR|
|»»» currency|GBP|
|»»» currency|CAD|
|»»» currency|AUD|

<h3 id="post_jobs_submit_multi_docs_jobtemplate-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|OK|None|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|Invalid request|None|
|401|[Unauthorized](https://tools.ietf.org/html/rfc7235#section-3.1)|Unauthorized|None|

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
bearerAuth
</aside>

## post_jobs_submit_multi_doc_merge_jobTemplate

<a id="opIdpost_jobs_submit_multi_doc_merge_jobTemplate"></a>

> Code samples

```shell
# You can also use wget
curl -X POST https://api.noname.com/jobs/submit/multi/doc/merge/jobTemplate \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer {access-token}'

```

```http
POST https://api.noname.com/jobs/submit/multi/doc/merge/jobTemplate HTTP/1.1
Host: api.noname.com
Content-Type: application/json

```

```javascript
const inputBody = '{
  "documentsToMerge": [
    {
      "documentId": "string"
    }
  ],
  "recipientAddressSource": {
    "firstName": "string",
    "lastName": "string",
    "nickName": "string",
    "address1": "string",
    "address2": "string",
    "address3": "string",
    "city": "string",
    "state": "string",
    "zip": "string",
    "country": "string",
    "phoneNumber": "string"
  },
  "jobTemplate": "string",
  "paymentDetails": {
    "billingType": "creditCard",
    "creditCardDetails": {
      "cardType": "visa",
      "cardNumber": "string",
      "expirationDate": {
        "month": 1,
        "year": 2000
      },
      "cvv": 0
    },
    "invoiceDetails": {
      "invoiceNumber": "string",
      "amountDue": 0
    },
    "achDetails": {
      "routingNumber": "string",
      "accountNumber": "string",
      "checkDigit": 0
    },
    "creditAmount": {
      "amount": 0,
      "currency": "USD"
    }
  },
  "tags": [
    "string"
  ]
}';
const headers = {
  'Content-Type':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('https://api.noname.com/jobs/submit/multi/doc/merge/jobTemplate',
{
  method: 'POST',
  body: inputBody,
  headers: headers
})
.then(function(res) {
    return res.json();
}).then(function(body) {
    console.log(body);
});

```

```ruby
require 'rest-client'
require 'json'

headers = {
  'Content-Type' => 'application/json',
  'Authorization' => 'Bearer {access-token}'
}

result = RestClient.post 'https://api.noname.com/jobs/submit/multi/doc/merge/jobTemplate',
  params: {
  }, headers: headers

p JSON.parse(result)

```

```python
import requests
headers = {
  'Content-Type': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.post('https://api.noname.com/jobs/submit/multi/doc/merge/jobTemplate', headers = headers)

print(r.json())

```

```php
<?php

require 'vendor/autoload.php';

$headers = array(
    'Content-Type' => 'application/json',
    'Authorization' => 'Bearer {access-token}',
);

$client = new \GuzzleHttp\Client();

// Define array of request body.
$request_body = array();

try {
    $response = $client->request('POST','https://api.noname.com/jobs/submit/multi/doc/merge/jobTemplate', array(
        'headers' => $headers,
        'json' => $request_body,
       )
    );
    print_r($response->getBody()->getContents());
 }
 catch (\GuzzleHttp\Exception\BadResponseException $e) {
    // handle exception or api errors.
    print_r($e->getMessage());
 }

 // ...

```

```java
URL obj = new URL("https://api.noname.com/jobs/submit/multi/doc/merge/jobTemplate");
HttpURLConnection con = (HttpURLConnection) obj.openConnection();
con.setRequestMethod("POST");
int responseCode = con.getResponseCode();
BufferedReader in = new BufferedReader(
    new InputStreamReader(con.getInputStream()));
String inputLine;
StringBuffer response = new StringBuffer();
while ((inputLine = in.readLine()) != null) {
    response.append(inputLine);
}
in.close();
System.out.println(response.toString());

```

```go
package main

import (
       "bytes"
       "net/http"
)

func main() {

    headers := map[string][]string{
        "Content-Type": []string{"application/json"},
        "Authorization": []string{"Bearer {access-token}"},
    }

    data := bytes.NewBuffer([]byte{jsonReq})
    req, err := http.NewRequest("POST", "https://api.noname.com/jobs/submit/multi/doc/merge/jobTemplate", data)
    req.Header = headers

    client := &http.Client{}
    resp, err := client.Do(req)
    // ...
}

```

`POST /jobs/submit/multi/doc/merge/jobTemplate`

*Merge documents, send to recipient using job template*

Merge documents, send to recipient using job template

> Body parameter

```json
{
  "documentsToMerge": [
    {
      "documentId": "string"
    }
  ],
  "recipientAddressSource": {
    "firstName": "string",
    "lastName": "string",
    "nickName": "string",
    "address1": "string",
    "address2": "string",
    "address3": "string",
    "city": "string",
    "state": "string",
    "zip": "string",
    "country": "string",
    "phoneNumber": "string"
  },
  "jobTemplate": "string",
  "paymentDetails": {
    "billingType": "creditCard",
    "creditCardDetails": {
      "cardType": "visa",
      "cardNumber": "string",
      "expirationDate": {
        "month": 1,
        "year": 2000
      },
      "cvv": 0
    },
    "invoiceDetails": {
      "invoiceNumber": "string",
      "amountDue": 0
    },
    "achDetails": {
      "routingNumber": "string",
      "accountNumber": "string",
      "checkDigit": 0
    },
    "creditAmount": {
      "amount": 0,
      "currency": "USD"
    }
  },
  "tags": [
    "string"
  ]
}
```

<h3 id="post_jobs_submit_multi_doc_merge_jobtemplate-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|object|true|none|
|» documentsToMerge|body|[oneOf]|true|none|
|»» *anonymous*|body|object|false|none|
|»»» documentId|body|string|true|none|
|»» *anonymous*|body|object|false|none|
|»»» externalUrl|body|string(uri)|true|none|
|»» *anonymous*|body|object|false|none|
|»»» uploadRequestId|body|string|true|none|
|»»» documentName|body|string|true|none|
|»» *anonymous*|body|object|false|none|
|»»» uploadRequestId|body|string|true|none|
|»»» zipId|body|string|true|none|
|»»» documentName|body|string|true|none|
|»» *anonymous*|body|object|false|none|
|»»» zipId|body|string|true|none|
|»»» documentName|body|string|true|none|
|» recipientAddressSource|body|any|true|none|
|»» *anonymous*|body|[RecipientAddress](#schemarecipientaddress)|false|none|
|»»» firstName|body|string|true|none|
|»»» lastName|body|string|true|none|
|»»» nickName|body|string|false|none|
|»»» address1|body|string|true|none|
|»»» address2|body|string|false|none|
|»»» address3|body|string|false|none|
|»»» city|body|string|true|none|
|»»» state|body|string|true|none|
|»»» zip|body|string|true|none|
|»»» country|body|string|true|none|
|»»» phoneNumber|body|string|false|none|
|»» *anonymous*|body|object|false|none|
|»»» addressListId|body|string|true|none|
|»» *anonymous*|body|object|false|none|
|»»» addressId|body|string|true|none|
|» jobTemplate|body|string|true|none|
|» paymentDetails|body|[PaymentDetails](#schemapaymentdetails)|false|none|
|»» billingType|body|string|true|none|
|»» creditCardDetails|body|[CreditCardDetails](#schemacreditcarddetails)|false|none|
|»»» cardType|body|string|true|none|
|»»» cardNumber|body|string|true|none|
|»»» expirationDate|body|object|true|none|
|»»»» month|body|integer|true|none|
|»»»» year|body|integer|true|none|
|»»» cvv|body|integer|true|none|
|»» invoiceDetails|body|object|false|none|
|»»» invoiceNumber|body|string|false|none|
|»»» amountDue|body|number|false|none|
|»» achDetails|body|[ACHDetails](#schemaachdetails)|false|none|
|»»» routingNumber|body|string|true|none|
|»»» accountNumber|body|string|true|none|
|»»» checkDigit|body|integer|true|none|
|»» creditAmount|body|[CreditAmount](#schemacreditamount)|false|none|
|»»» amount|body|number|true|none|
|»»» currency|body|string|true|none|
|» tags|body|[string]|false|none|

#### Enumerated Values

|Parameter|Value|
|---|---|
|»» billingType|creditCard|
|»» billingType|invoice|
|»» billingType|ach|
|»» billingType|userCredit|
|»»» cardType|visa|
|»»» cardType|mastercard|
|»»» cardType|discover|
|»»» cardType|americanExpress|
|»»» currency|USD|
|»»» currency|EUR|
|»»» currency|GBP|
|»»» currency|CAD|
|»»» currency|AUD|

<h3 id="post_jobs_submit_multi_doc_merge_jobtemplate-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|OK|None|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|Invalid request|None|
|401|[Unauthorized](https://tools.ietf.org/html/rfc7235#section-3.1)|Unauthorized|None|

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
bearerAuth
</aside>

## post_jobs_submit_single_pdf_split

<a id="opIdpost_jobs_submit_single_pdf_split"></a>

> Code samples

```shell
# You can also use wget
curl -X POST https://api.noname.com/jobs/submit/single/pdf/split \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer {access-token}'

```

```http
POST https://api.noname.com/jobs/submit/single/pdf/split HTTP/1.1
Host: api.noname.com
Content-Type: application/json

```

```javascript
const inputBody = '{
  "documentSourceIdentifier": {
    "documentId": "string"
  },
  "pageRanges": [
    {
      "startPage": 0,
      "endPage": 0,
      "recipientAddressSource": {
        "firstName": "string",
        "lastName": "string",
        "nickName": "string",
        "address1": "string",
        "address2": "string",
        "address3": "string",
        "city": "string",
        "state": "string",
        "zip": "string",
        "country": "string",
        "phoneNumber": "string"
      }
    }
  ],
  "paymentDetails": {
    "billingType": "creditCard",
    "creditCardDetails": {
      "cardType": "visa",
      "cardNumber": "string",
      "expirationDate": {
        "month": 1,
        "year": 2000
      },
      "cvv": 0
    },
    "invoiceDetails": {
      "invoiceNumber": "string",
      "amountDue": 0
    },
    "achDetails": {
      "routingNumber": "string",
      "accountNumber": "string",
      "checkDigit": 0
    },
    "creditAmount": {
      "amount": 0,
      "currency": "USD"
    }
  },
  "tags": [
    "string"
  ]
}';
const headers = {
  'Content-Type':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('https://api.noname.com/jobs/submit/single/pdf/split',
{
  method: 'POST',
  body: inputBody,
  headers: headers
})
.then(function(res) {
    return res.json();
}).then(function(body) {
    console.log(body);
});

```

```ruby
require 'rest-client'
require 'json'

headers = {
  'Content-Type' => 'application/json',
  'Authorization' => 'Bearer {access-token}'
}

result = RestClient.post 'https://api.noname.com/jobs/submit/single/pdf/split',
  params: {
  }, headers: headers

p JSON.parse(result)

```

```python
import requests
headers = {
  'Content-Type': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.post('https://api.noname.com/jobs/submit/single/pdf/split', headers = headers)

print(r.json())

```

```php
<?php

require 'vendor/autoload.php';

$headers = array(
    'Content-Type' => 'application/json',
    'Authorization' => 'Bearer {access-token}',
);

$client = new \GuzzleHttp\Client();

// Define array of request body.
$request_body = array();

try {
    $response = $client->request('POST','https://api.noname.com/jobs/submit/single/pdf/split', array(
        'headers' => $headers,
        'json' => $request_body,
       )
    );
    print_r($response->getBody()->getContents());
 }
 catch (\GuzzleHttp\Exception\BadResponseException $e) {
    // handle exception or api errors.
    print_r($e->getMessage());
 }

 // ...

```

```java
URL obj = new URL("https://api.noname.com/jobs/submit/single/pdf/split");
HttpURLConnection con = (HttpURLConnection) obj.openConnection();
con.setRequestMethod("POST");
int responseCode = con.getResponseCode();
BufferedReader in = new BufferedReader(
    new InputStreamReader(con.getInputStream()));
String inputLine;
StringBuffer response = new StringBuffer();
while ((inputLine = in.readLine()) != null) {
    response.append(inputLine);
}
in.close();
System.out.println(response.toString());

```

```go
package main

import (
       "bytes"
       "net/http"
)

func main() {

    headers := map[string][]string{
        "Content-Type": []string{"application/json"},
        "Authorization": []string{"Bearer {access-token}"},
    }

    data := bytes.NewBuffer([]byte{jsonReq})
    req, err := http.NewRequest("POST", "https://api.noname.com/jobs/submit/single/pdf/split", data)
    req.Header = headers

    client := &http.Client{}
    resp, err := client.Do(req)
    // ...
}

```

`POST /jobs/submit/single/pdf/split`

*Split a PDF into page ranges and send to different recipients*

Split a PDF into page ranges and send to different recipients

> Body parameter

```json
{
  "documentSourceIdentifier": {
    "documentId": "string"
  },
  "pageRanges": [
    {
      "startPage": 0,
      "endPage": 0,
      "recipientAddressSource": {
        "firstName": "string",
        "lastName": "string",
        "nickName": "string",
        "address1": "string",
        "address2": "string",
        "address3": "string",
        "city": "string",
        "state": "string",
        "zip": "string",
        "country": "string",
        "phoneNumber": "string"
      }
    }
  ],
  "paymentDetails": {
    "billingType": "creditCard",
    "creditCardDetails": {
      "cardType": "visa",
      "cardNumber": "string",
      "expirationDate": {
        "month": 1,
        "year": 2000
      },
      "cvv": 0
    },
    "invoiceDetails": {
      "invoiceNumber": "string",
      "amountDue": 0
    },
    "achDetails": {
      "routingNumber": "string",
      "accountNumber": "string",
      "checkDigit": 0
    },
    "creditAmount": {
      "amount": 0,
      "currency": "USD"
    }
  },
  "tags": [
    "string"
  ]
}
```

<h3 id="post_jobs_submit_single_pdf_split-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|object|true|none|
|» documentSourceIdentifier|body|any|true|none|
|»» *anonymous*|body|object|false|none|
|»»» documentId|body|string|true|none|
|»» *anonymous*|body|object|false|none|
|»»» externalUrl|body|string(uri)|true|none|
|»» *anonymous*|body|object|false|none|
|»»» uploadRequestId|body|string|true|none|
|»»» documentName|body|string|true|none|
|»» *anonymous*|body|object|false|none|
|»»» uploadRequestId|body|string|true|none|
|»»» zipId|body|string|true|none|
|»»» documentName|body|string|true|none|
|»» *anonymous*|body|object|false|none|
|»»» zipId|body|string|true|none|
|»»» documentName|body|string|true|none|
|» pageRanges|body|[object]|true|none|
|»» startPage|body|integer|true|none|
|»» endPage|body|integer|true|none|
|»» recipientAddressSource|body|any|true|none|
|»»» *anonymous*|body|[RecipientAddress](#schemarecipientaddress)|false|none|
|»»»» firstName|body|string|true|none|
|»»»» lastName|body|string|true|none|
|»»»» nickName|body|string|false|none|
|»»»» address1|body|string|true|none|
|»»»» address2|body|string|false|none|
|»»»» address3|body|string|false|none|
|»»»» city|body|string|true|none|
|»»»» state|body|string|true|none|
|»»»» zip|body|string|true|none|
|»»»» country|body|string|true|none|
|»»»» phoneNumber|body|string|false|none|
|»»» *anonymous*|body|object|false|none|
|»»»» addressListId|body|string|true|none|
|»»» *anonymous*|body|object|false|none|
|»»»» addressId|body|string|true|none|
|» paymentDetails|body|[PaymentDetails](#schemapaymentdetails)|false|none|
|»» billingType|body|string|true|none|
|»» creditCardDetails|body|[CreditCardDetails](#schemacreditcarddetails)|false|none|
|»»» cardType|body|string|true|none|
|»»» cardNumber|body|string|true|none|
|»»» expirationDate|body|object|true|none|
|»»»» month|body|integer|true|none|
|»»»» year|body|integer|true|none|
|»»» cvv|body|integer|true|none|
|»» invoiceDetails|body|object|false|none|
|»»» invoiceNumber|body|string|false|none|
|»»» amountDue|body|number|false|none|
|»» achDetails|body|[ACHDetails](#schemaachdetails)|false|none|
|»»» routingNumber|body|string|true|none|
|»»» accountNumber|body|string|true|none|
|»»» checkDigit|body|integer|true|none|
|»» creditAmount|body|[CreditAmount](#schemacreditamount)|false|none|
|»»» amount|body|number|true|none|
|»»» currency|body|string|true|none|
|» tags|body|[string]|false|none|

#### Enumerated Values

|Parameter|Value|
|---|---|
|»» billingType|creditCard|
|»» billingType|invoice|
|»» billingType|ach|
|»» billingType|userCredit|
|»»» cardType|visa|
|»»» cardType|mastercard|
|»»» cardType|discover|
|»»» cardType|americanExpress|
|»»» currency|USD|
|»»» currency|EUR|
|»»» currency|GBP|
|»»» currency|CAD|
|»»» currency|AUD|

<h3 id="post_jobs_submit_single_pdf_split-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|OK|None|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|Invalid request|None|
|401|[Unauthorized](https://tools.ietf.org/html/rfc7235#section-3.1)|Unauthorized|None|

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
bearerAuth
</aside>

## post_jobs_submit_single_pdf_split_addressCapture

<a id="opIdpost_jobs_submit_single_pdf_split_addressCapture"></a>

> Code samples

```shell
# You can also use wget
curl -X POST https://api.noname.com/jobs/submit/single/pdf/split/addressCapture \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer {access-token}'

```

```http
POST https://api.noname.com/jobs/submit/single/pdf/split/addressCapture HTTP/1.1
Host: api.noname.com
Content-Type: application/json

```

```javascript
const inputBody = '{
  "documentSourceIdentifier": {
    "documentId": "string"
  },
  "embeddedExtractionSpecs": [
    {
      "startPage": 0,
      "endPage": 0,
      "addressRegion": {
        "x": 0,
        "y": 0,
        "width": 0,
        "height": 0,
        "pageOffset": 0
      }
    }
  ],
  "paymentDetails": {
    "billingType": "creditCard",
    "creditCardDetails": {
      "cardType": "visa",
      "cardNumber": "string",
      "expirationDate": {
        "month": 1,
        "year": 2000
      },
      "cvv": 0
    },
    "invoiceDetails": {
      "invoiceNumber": "string",
      "amountDue": 0
    },
    "achDetails": {
      "routingNumber": "string",
      "accountNumber": "string",
      "checkDigit": 0
    },
    "creditAmount": {
      "amount": 0,
      "currency": "USD"
    }
  },
  "tags": [
    "string"
  ]
}';
const headers = {
  'Content-Type':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('https://api.noname.com/jobs/submit/single/pdf/split/addressCapture',
{
  method: 'POST',
  body: inputBody,
  headers: headers
})
.then(function(res) {
    return res.json();
}).then(function(body) {
    console.log(body);
});

```

```ruby
require 'rest-client'
require 'json'

headers = {
  'Content-Type' => 'application/json',
  'Authorization' => 'Bearer {access-token}'
}

result = RestClient.post 'https://api.noname.com/jobs/submit/single/pdf/split/addressCapture',
  params: {
  }, headers: headers

p JSON.parse(result)

```

```python
import requests
headers = {
  'Content-Type': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.post('https://api.noname.com/jobs/submit/single/pdf/split/addressCapture', headers = headers)

print(r.json())

```

```php
<?php

require 'vendor/autoload.php';

$headers = array(
    'Content-Type' => 'application/json',
    'Authorization' => 'Bearer {access-token}',
);

$client = new \GuzzleHttp\Client();

// Define array of request body.
$request_body = array();

try {
    $response = $client->request('POST','https://api.noname.com/jobs/submit/single/pdf/split/addressCapture', array(
        'headers' => $headers,
        'json' => $request_body,
       )
    );
    print_r($response->getBody()->getContents());
 }
 catch (\GuzzleHttp\Exception\BadResponseException $e) {
    // handle exception or api errors.
    print_r($e->getMessage());
 }

 // ...

```

```java
URL obj = new URL("https://api.noname.com/jobs/submit/single/pdf/split/addressCapture");
HttpURLConnection con = (HttpURLConnection) obj.openConnection();
con.setRequestMethod("POST");
int responseCode = con.getResponseCode();
BufferedReader in = new BufferedReader(
    new InputStreamReader(con.getInputStream()));
String inputLine;
StringBuffer response = new StringBuffer();
while ((inputLine = in.readLine()) != null) {
    response.append(inputLine);
}
in.close();
System.out.println(response.toString());

```

```go
package main

import (
       "bytes"
       "net/http"
)

func main() {

    headers := map[string][]string{
        "Content-Type": []string{"application/json"},
        "Authorization": []string{"Bearer {access-token}"},
    }

    data := bytes.NewBuffer([]byte{jsonReq})
    req, err := http.NewRequest("POST", "https://api.noname.com/jobs/submit/single/pdf/split/addressCapture", data)
    req.Header = headers

    client := &http.Client{}
    resp, err := client.Do(req)
    // ...
}

```

`POST /jobs/submit/single/pdf/split/addressCapture`

*Split PDF and extract embedded recipient addresses*

Split PDF and extract embedded recipient addresses

> Body parameter

```json
{
  "documentSourceIdentifier": {
    "documentId": "string"
  },
  "embeddedExtractionSpecs": [
    {
      "startPage": 0,
      "endPage": 0,
      "addressRegion": {
        "x": 0,
        "y": 0,
        "width": 0,
        "height": 0,
        "pageOffset": 0
      }
    }
  ],
  "paymentDetails": {
    "billingType": "creditCard",
    "creditCardDetails": {
      "cardType": "visa",
      "cardNumber": "string",
      "expirationDate": {
        "month": 1,
        "year": 2000
      },
      "cvv": 0
    },
    "invoiceDetails": {
      "invoiceNumber": "string",
      "amountDue": 0
    },
    "achDetails": {
      "routingNumber": "string",
      "accountNumber": "string",
      "checkDigit": 0
    },
    "creditAmount": {
      "amount": 0,
      "currency": "USD"
    }
  },
  "tags": [
    "string"
  ]
}
```

<h3 id="post_jobs_submit_single_pdf_split_addresscapture-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|object|true|none|
|» documentSourceIdentifier|body|any|true|none|
|»» *anonymous*|body|object|false|none|
|»»» documentId|body|string|true|none|
|»» *anonymous*|body|object|false|none|
|»»» externalUrl|body|string(uri)|true|none|
|»» *anonymous*|body|object|false|none|
|»»» uploadRequestId|body|string|true|none|
|»»» documentName|body|string|true|none|
|»» *anonymous*|body|object|false|none|
|»»» uploadRequestId|body|string|true|none|
|»»» zipId|body|string|true|none|
|»»» documentName|body|string|true|none|
|»» *anonymous*|body|object|false|none|
|»»» zipId|body|string|true|none|
|»»» documentName|body|string|true|none|
|» embeddedExtractionSpecs|body|[object]|true|none|
|»» startPage|body|integer|true|none|
|»» endPage|body|integer|true|none|
|»» addressRegion|body|object|true|none|
|»»» x|body|number|true|none|
|»»» y|body|number|true|none|
|»»» width|body|number|true|none|
|»»» height|body|number|true|none|
|»»» pageOffset|body|integer|true|none|
|» paymentDetails|body|[PaymentDetails](#schemapaymentdetails)|false|none|
|»» billingType|body|string|true|none|
|»» creditCardDetails|body|[CreditCardDetails](#schemacreditcarddetails)|false|none|
|»»» cardType|body|string|true|none|
|»»» cardNumber|body|string|true|none|
|»»» expirationDate|body|object|true|none|
|»»»» month|body|integer|true|none|
|»»»» year|body|integer|true|none|
|»»» cvv|body|integer|true|none|
|»» invoiceDetails|body|object|false|none|
|»»» invoiceNumber|body|string|false|none|
|»»» amountDue|body|number|false|none|
|»» achDetails|body|[ACHDetails](#schemaachdetails)|false|none|
|»»» routingNumber|body|string|true|none|
|»»» accountNumber|body|string|true|none|
|»»» checkDigit|body|integer|true|none|
|»» creditAmount|body|[CreditAmount](#schemacreditamount)|false|none|
|»»» amount|body|number|true|none|
|»»» currency|body|string|true|none|
|» tags|body|[string]|false|none|

#### Enumerated Values

|Parameter|Value|
|---|---|
|»» billingType|creditCard|
|»» billingType|invoice|
|»» billingType|ach|
|»» billingType|userCredit|
|»»» cardType|visa|
|»»» cardType|mastercard|
|»»» cardType|discover|
|»»» cardType|americanExpress|
|»»» currency|USD|
|»»» currency|EUR|
|»»» currency|GBP|
|»»» currency|CAD|
|»»» currency|AUD|

<h3 id="post_jobs_submit_single_pdf_split_addresscapture-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|OK|None|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|Invalid request|None|
|401|[Unauthorized](https://tools.ietf.org/html/rfc7235#section-3.1)|Unauthorized|None|

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
bearerAuth
</aside>

## post_jobs_submit_multi_pdf_addressCapture

<a id="opIdpost_jobs_submit_multi_pdf_addressCapture"></a>

> Code samples

```shell
# You can also use wget
curl -X POST https://api.noname.com/jobs/submit/multi/pdf/addressCapture \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer {access-token}'

```

```http
POST https://api.noname.com/jobs/submit/multi/pdf/addressCapture HTTP/1.1
Host: api.noname.com
Content-Type: application/json

```

```javascript
const inputBody = '{
  "addressCapturePdfs": [
    {
      "documentSourceIdentifier": {
        "documentId": "string"
      },
      "addressListRegion": {
        "x": 0,
        "y": 0,
        "width": 0,
        "height": 0,
        "pageOffset": 0
      },
      "delimiter": "string",
      "tags": [
        "string"
      ]
    }
  ],
  "jobTemplate": "string",
  "paymentDetails": {
    "billingType": "creditCard",
    "creditCardDetails": {
      "cardType": "visa",
      "cardNumber": "string",
      "expirationDate": {
        "month": 1,
        "year": 2000
      },
      "cvv": 0
    },
    "invoiceDetails": {
      "invoiceNumber": "string",
      "amountDue": 0
    },
    "achDetails": {
      "routingNumber": "string",
      "accountNumber": "string",
      "checkDigit": 0
    },
    "creditAmount": {
      "amount": 0,
      "currency": "USD"
    }
  },
  "tags": [
    "string"
  ]
}';
const headers = {
  'Content-Type':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('https://api.noname.com/jobs/submit/multi/pdf/addressCapture',
{
  method: 'POST',
  body: inputBody,
  headers: headers
})
.then(function(res) {
    return res.json();
}).then(function(body) {
    console.log(body);
});

```

```ruby
require 'rest-client'
require 'json'

headers = {
  'Content-Type' => 'application/json',
  'Authorization' => 'Bearer {access-token}'
}

result = RestClient.post 'https://api.noname.com/jobs/submit/multi/pdf/addressCapture',
  params: {
  }, headers: headers

p JSON.parse(result)

```

```python
import requests
headers = {
  'Content-Type': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.post('https://api.noname.com/jobs/submit/multi/pdf/addressCapture', headers = headers)

print(r.json())

```

```php
<?php

require 'vendor/autoload.php';

$headers = array(
    'Content-Type' => 'application/json',
    'Authorization' => 'Bearer {access-token}',
);

$client = new \GuzzleHttp\Client();

// Define array of request body.
$request_body = array();

try {
    $response = $client->request('POST','https://api.noname.com/jobs/submit/multi/pdf/addressCapture', array(
        'headers' => $headers,
        'json' => $request_body,
       )
    );
    print_r($response->getBody()->getContents());
 }
 catch (\GuzzleHttp\Exception\BadResponseException $e) {
    // handle exception or api errors.
    print_r($e->getMessage());
 }

 // ...

```

```java
URL obj = new URL("https://api.noname.com/jobs/submit/multi/pdf/addressCapture");
HttpURLConnection con = (HttpURLConnection) obj.openConnection();
con.setRequestMethod("POST");
int responseCode = con.getResponseCode();
BufferedReader in = new BufferedReader(
    new InputStreamReader(con.getInputStream()));
String inputLine;
StringBuffer response = new StringBuffer();
while ((inputLine = in.readLine()) != null) {
    response.append(inputLine);
}
in.close();
System.out.println(response.toString());

```

```go
package main

import (
       "bytes"
       "net/http"
)

func main() {

    headers := map[string][]string{
        "Content-Type": []string{"application/json"},
        "Authorization": []string{"Bearer {access-token}"},
    }

    data := bytes.NewBuffer([]byte{jsonReq})
    req, err := http.NewRequest("POST", "https://api.noname.com/jobs/submit/multi/pdf/addressCapture", data)
    req.Header = headers

    client := &http.Client{}
    resp, err := client.Do(req)
    // ...
}

```

`POST /jobs/submit/multi/pdf/addressCapture`

*Submit multiple PDFs with embedded address regions*

Submit multiple PDFs with embedded address regions

> Body parameter

```json
{
  "addressCapturePdfs": [
    {
      "documentSourceIdentifier": {
        "documentId": "string"
      },
      "addressListRegion": {
        "x": 0,
        "y": 0,
        "width": 0,
        "height": 0,
        "pageOffset": 0
      },
      "delimiter": "string",
      "tags": [
        "string"
      ]
    }
  ],
  "jobTemplate": "string",
  "paymentDetails": {
    "billingType": "creditCard",
    "creditCardDetails": {
      "cardType": "visa",
      "cardNumber": "string",
      "expirationDate": {
        "month": 1,
        "year": 2000
      },
      "cvv": 0
    },
    "invoiceDetails": {
      "invoiceNumber": "string",
      "amountDue": 0
    },
    "achDetails": {
      "routingNumber": "string",
      "accountNumber": "string",
      "checkDigit": 0
    },
    "creditAmount": {
      "amount": 0,
      "currency": "USD"
    }
  },
  "tags": [
    "string"
  ]
}
```

<h3 id="post_jobs_submit_multi_pdf_addresscapture-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|object|true|none|
|» addressCapturePdfs|body|[object]|true|none|
|»» documentSourceIdentifier|body|any|true|none|
|»»» *anonymous*|body|object|false|none|
|»»»» documentId|body|string|true|none|
|»»» *anonymous*|body|object|false|none|
|»»»» externalUrl|body|string(uri)|true|none|
|»»» *anonymous*|body|object|false|none|
|»»»» uploadRequestId|body|string|true|none|
|»»»» documentName|body|string|true|none|
|»»» *anonymous*|body|object|false|none|
|»»»» uploadRequestId|body|string|true|none|
|»»»» zipId|body|string|true|none|
|»»»» documentName|body|string|true|none|
|»»» *anonymous*|body|object|false|none|
|»»»» zipId|body|string|true|none|
|»»»» documentName|body|string|true|none|
|»» addressListRegion|body|object|true|none|
|»»» x|body|number|true|none|
|»»» y|body|number|true|none|
|»»» width|body|number|true|none|
|»»» height|body|number|true|none|
|»»» pageOffset|body|integer|true|none|
|»» delimiter|body|string|false|none|
|»» tags|body|[string]|false|none|
|» jobTemplate|body|string|true|none|
|» paymentDetails|body|[PaymentDetails](#schemapaymentdetails)|false|none|
|»» billingType|body|string|true|none|
|»» creditCardDetails|body|[CreditCardDetails](#schemacreditcarddetails)|false|none|
|»»» cardType|body|string|true|none|
|»»» cardNumber|body|string|true|none|
|»»» expirationDate|body|object|true|none|
|»»»» month|body|integer|true|none|
|»»»» year|body|integer|true|none|
|»»» cvv|body|integer|true|none|
|»» invoiceDetails|body|object|false|none|
|»»» invoiceNumber|body|string|false|none|
|»»» amountDue|body|number|false|none|
|»» achDetails|body|[ACHDetails](#schemaachdetails)|false|none|
|»»» routingNumber|body|string|true|none|
|»»» accountNumber|body|string|true|none|
|»»» checkDigit|body|integer|true|none|
|»» creditAmount|body|[CreditAmount](#schemacreditamount)|false|none|
|»»» amount|body|number|true|none|
|»»» currency|body|string|true|none|
|» tags|body|[string]|false|none|

#### Enumerated Values

|Parameter|Value|
|---|---|
|»» billingType|creditCard|
|»» billingType|invoice|
|»» billingType|ach|
|»» billingType|userCredit|
|»»» cardType|visa|
|»»» cardType|mastercard|
|»»» cardType|discover|
|»»» cardType|americanExpress|
|»»» currency|USD|
|»»» currency|EUR|
|»»» currency|GBP|
|»»» currency|CAD|
|»»» currency|AUD|

<h3 id="post_jobs_submit_multi_pdf_addresscapture-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|OK|None|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|Invalid request|None|
|401|[Unauthorized](https://tools.ietf.org/html/rfc7235#section-3.1)|Unauthorized|None|

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
bearerAuth
</aside>

<h1 id="click2mail-document-submission-api-webhooks">webhooks</h1>

Operations related to webhooks

## post_webhooks_jobStatusUpdate

<a id="opIdpost_webhooks_jobStatusUpdate"></a>

> Code samples

```shell
# You can also use wget
curl -X POST https://api.noname.com/webhooks/jobStatusUpdate \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -H 'Authorization: Bearer {access-token}'

```

```http
POST https://api.noname.com/webhooks/jobStatusUpdate HTTP/1.1
Host: api.noname.com
Content-Type: application/json
Accept: application/json

```

```javascript
const inputBody = '{
  "jobId": "job_123456789",
  "status": "completed",
  "timestamp": "2025-07-07T12:34:56Z",
  "metadata": {
    "source": "PrintCenterA",
    "batch": "B20250707"
  }
}';
const headers = {
  'Content-Type':'application/json',
  'Accept':'application/json',
  'Authorization':'Bearer {access-token}'
};

fetch('https://api.noname.com/webhooks/jobStatusUpdate',
{
  method: 'POST',
  body: inputBody,
  headers: headers
})
.then(function(res) {
    return res.json();
}).then(function(body) {
    console.log(body);
});

```

```ruby
require 'rest-client'
require 'json'

headers = {
  'Content-Type' => 'application/json',
  'Accept' => 'application/json',
  'Authorization' => 'Bearer {access-token}'
}

result = RestClient.post 'https://api.noname.com/webhooks/jobStatusUpdate',
  params: {
  }, headers: headers

p JSON.parse(result)

```

```python
import requests
headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  'Authorization': 'Bearer {access-token}'
}

r = requests.post('https://api.noname.com/webhooks/jobStatusUpdate', headers = headers)

print(r.json())

```

```php
<?php

require 'vendor/autoload.php';

$headers = array(
    'Content-Type' => 'application/json',
    'Accept' => 'application/json',
    'Authorization' => 'Bearer {access-token}',
);

$client = new \GuzzleHttp\Client();

// Define array of request body.
$request_body = array();

try {
    $response = $client->request('POST','https://api.noname.com/webhooks/jobStatusUpdate', array(
        'headers' => $headers,
        'json' => $request_body,
       )
    );
    print_r($response->getBody()->getContents());
 }
 catch (\GuzzleHttp\Exception\BadResponseException $e) {
    // handle exception or api errors.
    print_r($e->getMessage());
 }

 // ...

```

```java
URL obj = new URL("https://api.noname.com/webhooks/jobStatusUpdate");
HttpURLConnection con = (HttpURLConnection) obj.openConnection();
con.setRequestMethod("POST");
int responseCode = con.getResponseCode();
BufferedReader in = new BufferedReader(
    new InputStreamReader(con.getInputStream()));
String inputLine;
StringBuffer response = new StringBuffer();
while ((inputLine = in.readLine()) != null) {
    response.append(inputLine);
}
in.close();
System.out.println(response.toString());

```

```go
package main

import (
       "bytes"
       "net/http"
)

func main() {

    headers := map[string][]string{
        "Content-Type": []string{"application/json"},
        "Accept": []string{"application/json"},
        "Authorization": []string{"Bearer {access-token}"},
    }

    data := bytes.NewBuffer([]byte{jsonReq})
    req, err := http.NewRequest("POST", "https://api.noname.com/webhooks/jobStatusUpdate", data)
    req.Header = headers

    client := &http.Client{}
    resp, err := client.Do(req)
    // ...
}

```

`POST /webhooks/jobStatusUpdate`

*Webhook endpoint to receive job status updates*

Webhook endpoint to receive job status updates

> Body parameter

```json
{
  "jobId": "job_123456789",
  "status": "completed",
  "timestamp": "2025-07-07T12:34:56Z",
  "metadata": {
    "source": "PrintCenterA",
    "batch": "B20250707"
  }
}
```

<h3 id="post_webhooks_jobstatusupdate-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|object|true|none|
|» jobId|body|string|true|none|
|» status|body|string|true|none|
|» timestamp|body|string(date-time)|true|none|
|» metadata|body|object|false|none|
|»» **additionalProperties**|body|string|false|none|

#### Enumerated Values

|Parameter|Value|
|---|---|
|» status|queued|
|» status|processing|
|» status|completed|
|» status|failed|

> Example responses

> 200 Response

```json
{
  "status": "string",
  "message": "string",
  "jobId": "string"
}
```

<h3 id="post_webhooks_jobstatusupdate-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Webhook received successfully|[StandardResponse](#schemastandardresponse)|
|400|[Bad Request](https://tools.ietf.org/html/rfc7231#section-6.5.1)|Invalid payload|None|
|401|[Unauthorized](https://tools.ietf.org/html/rfc7235#section-3.1)|Unauthorized|None|

<aside class="warning">
To perform this operation, you must be authenticated by means of one of the following methods:
bearerAuth
</aside>

# Schemas

<h2 id="tocS_DocumentSourceIdentifier">DocumentSourceIdentifier</h2>
<!-- backwards compatibility -->
<a id="schemadocumentsourceidentifier"></a>
<a id="schema_DocumentSourceIdentifier"></a>
<a id="tocSdocumentsourceidentifier"></a>
<a id="tocsdocumentsourceidentifier"></a>

```json
{
  "documentId": "string"
}

```

### Properties

oneOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|*anonymous*|object|false|none|none|
|» documentId|string|true|none|none|

xor

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|*anonymous*|object|false|none|none|
|» externalUrl|string(uri)|true|none|none|

xor

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|*anonymous*|object|false|none|none|
|» uploadRequestId|string|true|none|none|
|» documentName|string|true|none|none|

xor

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|*anonymous*|object|false|none|none|
|» uploadRequestId|string|true|none|none|
|» zipId|string|true|none|none|
|» documentName|string|true|none|none|

xor

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|*anonymous*|object|false|none|none|
|» zipId|string|true|none|none|
|» documentName|string|true|none|none|

<h2 id="tocS_RecipientAddress">RecipientAddress</h2>
<!-- backwards compatibility -->
<a id="schemarecipientaddress"></a>
<a id="schema_RecipientAddress"></a>
<a id="tocSrecipientaddress"></a>
<a id="tocsrecipientaddress"></a>

```json
{
  "firstName": "string",
  "lastName": "string",
  "nickName": "string",
  "address1": "string",
  "address2": "string",
  "address3": "string",
  "city": "string",
  "state": "string",
  "zip": "string",
  "country": "string",
  "phoneNumber": "string"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|firstName|string|true|none|none|
|lastName|string|true|none|none|
|nickName|string|false|none|none|
|address1|string|true|none|none|
|address2|string|false|none|none|
|address3|string|false|none|none|
|city|string|true|none|none|
|state|string|true|none|none|
|zip|string|true|none|none|
|country|string|true|none|none|
|phoneNumber|string|false|none|none|

<h2 id="tocS_RecipientAddressSource">RecipientAddressSource</h2>
<!-- backwards compatibility -->
<a id="schemarecipientaddresssource"></a>
<a id="schema_RecipientAddressSource"></a>
<a id="tocSrecipientaddresssource"></a>
<a id="tocsrecipientaddresssource"></a>

```json
{
  "firstName": "string",
  "lastName": "string",
  "nickName": "string",
  "address1": "string",
  "address2": "string",
  "address3": "string",
  "city": "string",
  "state": "string",
  "zip": "string",
  "country": "string",
  "phoneNumber": "string"
}

```

### Properties

oneOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|*anonymous*|[RecipientAddress](#schemarecipientaddress)|false|none|none|

xor

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|*anonymous*|object|false|none|none|
|» addressListId|string|true|none|none|

xor

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|*anonymous*|object|false|none|none|
|» addressId|string|true|none|none|

<h2 id="tocS_JobOptions">JobOptions</h2>
<!-- backwards compatibility -->
<a id="schemajoboptions"></a>
<a id="schema_JobOptions"></a>
<a id="tocSjoboptions"></a>
<a id="tocsjoboptions"></a>

```json
{
  "documentClass": "businessLetter",
  "layout": "portrait",
  "mailclass": "firstClassMail",
  "paperType": "letter",
  "printOption": "none",
  "envelope": "flat"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|documentClass|string|true|none|none|
|layout|string|true|none|none|
|mailclass|string|true|none|none|
|paperType|string|true|none|none|
|printOption|string|true|none|none|
|envelope|string|true|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|documentClass|businessLetter|
|documentClass|personalLetter|
|layout|portrait|
|layout|landscape|
|mailclass|firstClassMail|
|mailclass|priorityMail|
|mailclass|largeEnvelope|
|paperType|letter|
|paperType|legal|
|paperType|postcard|
|printOption|none|
|printOption|color|
|printOption|grayscale|
|envelope|flat|
|envelope|windowedFlat|
|envelope|letter|
|envelope|legal|
|envelope|postcard|

<h2 id="tocS_CreditCardDetails">CreditCardDetails</h2>
<!-- backwards compatibility -->
<a id="schemacreditcarddetails"></a>
<a id="schema_CreditCardDetails"></a>
<a id="tocScreditcarddetails"></a>
<a id="tocscreditcarddetails"></a>

```json
{
  "cardType": "visa",
  "cardNumber": "string",
  "expirationDate": {
    "month": 1,
    "year": 2000
  },
  "cvv": 0
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|cardType|string|true|none|none|
|cardNumber|string|true|none|none|
|expirationDate|object|true|none|none|
|» month|integer|true|none|none|
|» year|integer|true|none|none|
|cvv|integer|true|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|cardType|visa|
|cardType|mastercard|
|cardType|discover|
|cardType|americanExpress|

<h2 id="tocS_ACHDetails">ACHDetails</h2>
<!-- backwards compatibility -->
<a id="schemaachdetails"></a>
<a id="schema_ACHDetails"></a>
<a id="tocSachdetails"></a>
<a id="tocsachdetails"></a>

```json
{
  "routingNumber": "string",
  "accountNumber": "string",
  "checkDigit": 0
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|routingNumber|string|true|none|none|
|accountNumber|string|true|none|none|
|checkDigit|integer|true|none|none|

<h2 id="tocS_CreditAmount">CreditAmount</h2>
<!-- backwards compatibility -->
<a id="schemacreditamount"></a>
<a id="schema_CreditAmount"></a>
<a id="tocScreditamount"></a>
<a id="tocscreditamount"></a>

```json
{
  "amount": 0,
  "currency": "USD"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|amount|number|true|none|none|
|currency|string|true|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|currency|USD|
|currency|EUR|
|currency|GBP|
|currency|CAD|
|currency|AUD|

<h2 id="tocS_PaymentDetails">PaymentDetails</h2>
<!-- backwards compatibility -->
<a id="schemapaymentdetails"></a>
<a id="schema_PaymentDetails"></a>
<a id="tocSpaymentdetails"></a>
<a id="tocspaymentdetails"></a>

```json
{
  "billingType": "creditCard",
  "creditCardDetails": {
    "cardType": "visa",
    "cardNumber": "string",
    "expirationDate": {
      "month": 1,
      "year": 2000
    },
    "cvv": 0
  },
  "invoiceDetails": {
    "invoiceNumber": "string",
    "amountDue": 0
  },
  "achDetails": {
    "routingNumber": "string",
    "accountNumber": "string",
    "checkDigit": 0
  },
  "creditAmount": {
    "amount": 0,
    "currency": "USD"
  }
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|billingType|string|true|none|none|
|creditCardDetails|[CreditCardDetails](#schemacreditcarddetails)|false|none|none|
|invoiceDetails|object|false|none|none|
|» invoiceNumber|string|false|none|none|
|» amountDue|number|false|none|none|
|achDetails|[ACHDetails](#schemaachdetails)|false|none|none|
|creditAmount|[CreditAmount](#schemacreditamount)|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|billingType|creditCard|
|billingType|invoice|
|billingType|ach|
|billingType|userCredit|

<h2 id="tocS_StandardResponse">StandardResponse</h2>
<!-- backwards compatibility -->
<a id="schemastandardresponse"></a>
<a id="schema_StandardResponse"></a>
<a id="tocSstandardresponse"></a>
<a id="tocsstandardresponse"></a>

```json
{
  "status": "string",
  "message": "string",
  "jobId": "string"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|status|string|false|none|none|
|message|string|false|none|none|
|jobId|string|false|none|none|

