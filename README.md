# state-example

How to manage user state through oauth redirect flows.

## Concepts

* client already store user information
* the user is the owner of the resource i.e. financial data
* client wants to identify the user through the redirect flow

## User stories

> As a client, I want to be able to track if a user of my platform has given me consent to access his financial data, so that I can use that to further provide services to that user.

Scenario:

1. Client MegaCorp wants to access User Alice's financial data
2. MegaCorp redirects Alice to TrueLayer's consent dialog
3. Alice gives consent to access their financial data
4. TrueLayer submits a `code` to MegaCorp's `redirect_uri`
5. MegaCorp exchanges that `code` for a token
6. MegaCorp can now use that token to retrieve Alice's financial data

The endpoint which the `redirect_uri` refers to in step #4, will be called multiple times for every user that has given consent so:

> How can I, as a client, keep track of which code corresponds to each of my user's consent?

This is what the `state` query parameter in the authentication link is for. The value of the `state` parameter is replayed to the client, at the moment the `redirect_uri` is called.

The value can be used to correlate the received `code` with the known user.

The content is a completely opaque structure, from the perspective of TrueLayer's platform, meaning it won't be modified or augmented in any way.

## Example

The client can encode (using base64 for example) the user ID as the state value.

This code example shows exactly that scenario. There are 3 users with different IDs in a DB, and you can choose any of them to take through the consent flow. 

In the end, the code received when the `redirect_uri` is called, can be mapped to the corresponding user by decoding the state parameter.

## Running this example

Install the project dependencies by running `make install`.

You can run the project by specifying your TrueLayer `client_id` and `client_secret` as environment variables, e.g.

```
CLIENT_ID=<tl_client_id> \
CLIENT_SECRET=<tl_client_secret> \
REDIRECT_URI=http://localhost:3000/callback \
make run
```

Note that **you need to allow** `http://localhost:3000/callback` as a valid `redirect_uri` in the TrueLayer Console.

