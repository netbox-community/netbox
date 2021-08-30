/**
 * Rather than use CDNs to include GraphiQL dependencies, import and bundle the dependencies so
 * they can be locally served.
 */

import * as React from 'react';
import * as ReactDOM from 'react-dom';
import 'graphql';
import GraphiQL from 'graphiql';
import SubscriptionsTransportWs from 'subscriptions-transport-ws';

window.React = React;
window.ReactDOM = ReactDOM;
// @ts-expect-error Assigning to window is required for graphene-django
window.SubscriptionsTransportWs = SubscriptionsTransportWs;
// @ts-expect-error Assigning to window is required for graphene-django
window.GraphiQL = GraphiQL;
