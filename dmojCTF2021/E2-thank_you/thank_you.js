/* 
 * This is a custom version of V8 that adds six functions in order to perform I/O and aid in online judging.
 *
 * * `print(...)`: similar to Python's `print`, prints all argument separated by space followed by new line.
 * * `flush()`: flushes stdout, ensuring everything output by `print()` immediately shows up.
 * * `gets()`: similar to the Ruby equivalent, returns one line of input from `stdin`.
 * * `read(bytes)`: read `bytes` bytes from stdin as an `ArrayBuffer`.
 * * `write(buffer)`: write a typed array, `ArrayBuffer`, or a view of `ArrayBuffer` to stdout.
 * * `quit(code)`: exits the program with `code`.
 * * You can also assign to the global variable `autoflush` to control whether `print()` flushes.
 *
 */

autoflush = true;

const users = {
	'flag': {
		restricted: false,
		information: '<flag>',
		name: '<secret>',
	},
	'user': {
		restricted: true,
		information: 'I am a user account!',
		name: 'User'
	}
}

let current_user = null;

while(true) {
	print('Welcome to the TY book store!');
	print('Please select an option:');
	print('1. Login');
	print('2. Get User Data (non-restricted users only)');
	print('3. Exit');

	let command = gets();
	if (command === '1') {
		print('What username?');
		let user = gets();
		print('Security question: what is your name?');
		let name = gets();
		if (users[user].name !== name) {
			print('Security check failed');
			break;
		}
		current_user = user;
		print('Successfully logged in.');
	} else if (command === '2') {
		if (typeof current_user !== 'string' || users[current_user].restricted) {
			print('User unauthorized.');
			break;
		}
		print('Which user would you like to get user data about?');
		let user = gets();
		throw new Error(JSON.stringify(users[user]));
	} else {
		break;
	}
}