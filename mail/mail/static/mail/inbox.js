document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);
  document.querySelector('#compose-form').addEventListener('submit',send_email);

  // By default, load the inbox
  load_mailbox('inbox');
});

function load_mailbox(mailbox) {
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#get-email').innerHTML = '';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  fetch(`/emails/${mailbox}`, {
    method: 'GET',
  })
  .then(response => response.json())
  .then(emails => {
    console.log(emails);
    const email_view = document.getElementById('emails-view');

    emails.forEach(item => {
      let shouldShow = false;
      let buttonText = ''; // Text for the archive/unarchive button
      if (mailbox === 'archive') {
        shouldShow = item.archived;
        buttonText = 'Unarchive';
      } else if (mailbox === 'inbox') {
        shouldShow = !item.archived;
        buttonText = 'Archive';
      } else if (mailbox === 'sent') {
        shouldShow = true; // Always show in sent, but without archive button
      }
    
      if (shouldShow) {
        const email_div = document.createElement('div');
        email_div.classList.add('email-summary');
        email_div.innerHTML = `
        <div class="email-item-container">
          <div class="mail-list-container">
            <span class="mail-float-start">${item.sender}</span>
            <span class="mail-float-mid">${item.subject}</span>
            <span class="mail-float-end">${item.timestamp}</span>
          </div>
        </div>`;
    
        if (mailbox === 'inbox' || mailbox === 'archive') {
          const button = document.createElement('button');
          button.textContent = buttonText;
          button.addEventListener('click', (e) => {
            e.stopPropagation(); // Prevent triggering the email open action
            toggleArchiveStatus(item.id, item.archived);
          });
          email_div.appendChild(button);
        }
    
        email_div.addEventListener('click', () => get_email(item.id));
        email_view.appendChild(email_div);
      }
    });
    
  });
}

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';
  document.querySelector('#get-email').innerHTML = '';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function send_email(event) {

  event.preventDefault();
  let body = document.querySelector('#compose-body').value
  let recipients = document.querySelector('#compose-recipients').value
  let subject = document.querySelector('#compose-subject').value

  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
        recipients: recipients,
        subject: subject,
        body: body
    })
  })
  .then(response => response.json())
  .then(result => {
      // Print result
      console.log(result);
      load_mailbox('sent')
  });
}

function get_email(email_id) {

  document.querySelector('#emails-view').style.display = 'none';
  fetch(`/emails/${email_id}`, {
  method: 'GET'
})
.then(response => response.json())
.then(email_id=> {console.log(email_id);
  return email_id;
  })
  
  .then(email => {
    const get_email = document.getElementById('get-email');
    get_email.innerHTML = `
    <h3>${email.subject}</h3>
    <div id="email-sender">From: ${email.sender}</div>
    <div id="email-recipients">To: ${email.recipients}</div>
    <div id="email-body">${email.body}</div>

    <button class="reply-btn">Reply</button>

    `
    document.querySelector('.reply-btn').addEventListener('click', () => reply_email(email));

  });

  fetch(`/emails/${email_id}`,{
    method: 'PUT',
    body : JSON.stringify({
      read:true
    })
    
  })
}

function toggleArchiveStatus(email_id, currentlyArchived) {
  fetch(`/emails/${email_id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      archived: !currentlyArchived
    })
  })
  .then(response => {
    if (response.ok) {
      // Determine which mailbox to load based on the current archived status
      const mailboxToLoad = currentlyArchived ? 'archive' : 'inbox';
      load_mailbox(mailboxToLoad);
    } else {
      alert('There was an error updating the email.');
    }
  });
}

function reply_email(email) {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';
  document.querySelector('#get-email').innerHTML = '';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = `${email.sender}`;
  document.querySelector('#compose-subject').value = `Re: ${email.subject}`;
  document.querySelector('#compose-body').value = `On ${email.timestamp} ${email.sender} wrote:
  ${email.body}`;
}