Feature: STMTS publishing and reading
  Scenario: Long form remains readable
    Given an authenticated reader at 390 CSS pixels in either theme
    When a 40,000 character statement with images, tables and code is opened
    Then paragraphs wrap without page-level horizontal scrolling
    And tables and code scroll within labeled containers
    And back returns to the original feed anchor

  Scenario: Save recovery after a network loss
    Given a draft has unsynced text and the network becomes unavailable
    When the user continues typing
    Then the draft is saved locally within 500ms of inactivity
    And the status says Saved on this device
    And publishing remains unavailable with an explanation
    When connectivity returns
    Then remote save uses the current revision
    And a conflict preserves both versions rather than overwriting either

  Scenario: Publish cannot duplicate
    Given the latest source has a valid server preview and ready media
    When Publish is tapped twice and the first response is lost
    Then one idempotency key is reused until outcome is known
    And the server creates exactly one public post
    And the draft is removed only after confirmed success

  Scenario: Source is not executable
    Given a draft contains a script tag, an event-handler image and a javascript link
    When previewed or published on any client
    Then none of the payloads execute or load unauthorized resources
    And unsupported HTML appears as escaped literal text
    And invalid links show safe text with validation feedback

  Scenario: Media must be accessible and ready
    Given a draft has an image without alt text or a decorative designation
    And a video is still processing
    When publish eligibility is calculated
    Then the action is disabled with visible reasons
    And retry or remove is available for failed attachments
    And adding video to a draft with images is rejected before upload

  Scenario: Platform accessibility
    Given the largest supported native text size or 200 percent web text enlargement
    When the user navigates using VoiceOver, TalkBack or keyboard
    Then each control has a name and state and content remains unclipped
    And dialogs trap and restore focus on web and dismiss through native back
    And reduced motion removes nonessential animation

  Scenario: Reaction fails
    Given a post is initially unliked with count 12
    When the reader likes it and the server rejects the request
    Then the client restores unliked and count 12
    And politely announces failure and exposes Retry

  Scenario: Reading a removed post
    Given a bookmarked post has been deleted
    When the user opens the bookmark or an old deep link
    Then no body or media is rendered
    And a neutral unavailable view offers a return path

  Scenario: No autoplay
    Given a feed contains a ready video and data saver is enabled
    When the video card enters the viewport
    Then only an appropriately sized poster is requested
    And no sound or video playback begins until Play is activated

  Scenario: Account isolation
    Given account A has an unsynced local draft
    When account A signs out and account B signs in
    Then account B cannot see or publish account A's draft
    And account A received a warning before unsynced data was discarded

  Scenario: Three client render parity
    Given fixtures in markdown-fixtures.json
    When web, iOS and Android render the canonical block tree
    Then structure and visible text match the fixture expectations
    And all attachment lookups enforce authorization

  Scenario: Profile and discovery navigation
    Given an empty Following feed
    When the reader opens Discover and follows an author
    Then the selected follow state reconciles with the server
    And the author's eligible posts appear after Following refresh
    And a failed follow restores the prior state
