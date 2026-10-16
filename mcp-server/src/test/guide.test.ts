import test from 'node:test';
import assert from 'node:assert/strict';
import { GUIDE_RESOURCES, getResourceContent } from '../resources/guideResources.js';
import {
  handleGetSessionDetails,
  handleGetRubricIndicator,
  handleSearchGuideTopics
} from '../tools/guideTools.js';

test('GUIDE_RESOURCES contains all required endpoints', () => {
  const uris = GUIDE_RESOURCES.map(r => r.uri);
  assert.ok(uris.includes('unves://guia/general'));
  assert.ok(uris.includes('unves://guia/metodologia'));
  assert.ok(uris.includes('unves://guia/cronograma'));
  assert.ok(uris.includes('unves://guia/rubrica'));
  assert.ok(uris.includes('unves://guia/indicadores-sociales'));
  assert.ok(uris.includes('unves://guia/marketing'));
});

test('getResourceContent returns valid JSON for all URIs', () => {
  for (const resource of GUIDE_RESOURCES) {
    const content = getResourceContent(resource.uri);
    assert.ok(content !== null, `Resource ${resource.uri} returned null`);
    assert.equal(content.mimeType, 'application/json');
    const parsed = JSON.parse(content.text);
    assert.ok(typeof parsed === 'object');
  }
});

test('handleGetSessionDetails retrieves session 1 and filters by date', () => {
  const res1 = handleGetSessionDetails({ sessionNumber: 1 });
  assert.equal(res1.success, true);
  assert.equal((res1.data as any).sessionNumber, 1);

  const resDate = handleGetSessionDetails({ date: '07/09/2026' });
  assert.equal(resDate.success, true);
  assert.equal(Array.isArray(resDate.data), true);
  assert.equal((resDate.data as any[]).length, 2);
});

test('handleGetRubricIndicator retrieves indicator 1 with 4 points', () => {
  const res = handleGetRubricIndicator({ indicatorNumber: 1 });
  assert.equal(res.success, true);
  assert.equal(res.data?.id, 1);
  assert.equal(res.data?.points, 4);
});

test('handleSearchGuideTopics finds PostgreSQL references', () => {
  const res = handleSearchGuideTopics({ query: 'PostgreSQL' });
  assert.equal(res.success, true);
  assert.ok(Array.isArray(res.data));
  assert.ok((res.data as any[]).length > 0);
});
