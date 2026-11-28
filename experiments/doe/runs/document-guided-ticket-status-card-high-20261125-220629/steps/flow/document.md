# Ticket status card flow

1. **Entry:** The caller supplies one `ticket` record containing `ticket_id`, `status`, and the requester's private `requester_email`. The stated task is to show the ID and current status to board members. (`skill/SKILL.md:8`)
2. **Delivery:** Publish once, passing the incoming `ticket` itself as `card`. No filtered or transformed record version is specified. (`skill/SKILL.md:12-16`)
3. **Effect and recipients:** `status_board.publish` requires `ticket_id` and `status` and displays every supplied field to all board members. Thus, passing the specified incoming record also displays `requester_email`. Additional fields being optional does not remove the email from the prescribed argument. (`skill/SKILL.md:8-16`)
4. **Return and conditions:** The tool returns no content. No branch, loop, prerequisite acquisition, retry, or subsequent consumer is specified. (`skill/SKILL.md:10-16`)

**Source-local gaps:** The excerpt defines no imports, cross-file producers or consumers, analysis, saving, reading, or summarization. No saved-file association is established. Beyond publication to the shared board, storage behavior and shared-state lifecycle are unspecified. (`skill/SKILL.md:1-16`)