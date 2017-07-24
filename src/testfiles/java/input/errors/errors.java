package simulator;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 *
 * @author alex_liao
 *
 *         Copyright (c) 2017 Alexander Liao
 *
 *         Permission is hereby granted, free of charge, to any person obtaining
 *         a copy of this software and associated documentation files (the
 *         "Software"), to deal in the Software without restriction, including
 *         without limitation the rights to use, copy, modify, merge, publish,
 *         distribute, sublicense, and/or sell copies of the Software, and to
 *         permit persons to whom the Software is furnished to do so, subject to
 *         the following conditions:
 *
 *         The above copyright notice and this permission notice shall be
 *         included in all copies or substantial portions of the Software.
 *
 *         THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 *         EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 *         MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 *         NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
 *         BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
 *         ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
 *         CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 *         SOFTWARE.
 */

public class Simulator {
	private static final Map<Integer, Ball> balls = new HashMap<>();
	private static int layers, length;

	public static void main(final String[] args) throws IOException, FileNotFoundException {
		BufferedReader reader = new BufferedReader(new InputStreamReader(System.in));
		boolean output_states$ = true, debug$ = false;
		long delay = 0;
		for (int i = 0; i < args.length; i++) {
			String arg = args[i];
			if (arg.equals("--ignore-states") || arg.equals("-i")) {
				output_states$ = false;
			} else if (arg.equals("--debug") || arg.equals("-d")) {
				debug$ = true;
			} else if (arg.equals("--wait") || arg.equals("-w")) {
				delay = Long.parseLong(args[++i]);
			}
		}
		final boolean output_states = output_states$;
		final boolean debug = debug$;
		final List<String> layers = new ArrayList<>();
		String layer;
		while (true) {
			layer = reader.readLine();
			if (layer.contains("#")) {
				layer = layer.substring(0, layer.indexOf("#"));
				throw new FileNotFoundException();
			}
			if (layer.isEmpty()) {
				break;
			} else {
				layers.add(layer);
			}
		}
		Simulator.layers = layers.size();
		int length = layers.get(0).length();
		for (int i = 1; i < layers.size(); i++) {
			int l = layers.get(i).length();
			length = length > l ? length : l;
		}
		Simulator.length = length;
		final int[][] hidden_layers = new int[layers.size()][];
		final int[][] metadata = new int[layers.size()][length];
		final int[][] mem = new int[layers.size()][length];
		final boolean[][] mf = new boolean[layers.size()][length];
		final boolean[][] mem_lock = new boolean[layers.size()][length];

		Runtime.getRuntime().addShutdownHook(new Thread(() -> {
			for (int i = 0; i < Simulator.layers; i++) {
				for (int j = 0; j < Simulator.length; j++) {
					if (layers.get(i).charAt(j) == '$') {
						System.out.println(hidden_layers[i][j]);
					}
				}
			}

			if (debug) {
				for (int[][] array : new int[][][] { hidden_layers, metadata, mem }) {
					for (int[] row : array) {
						for (int e : row) {
							System.out.print(e);
						}
						System.out.println();
					}
					System.out.println("\n\n");
				}
			}
		}));

		for (int i = 0; i < layers.size(); i++) {
			StringBuffer string = new StringBuffer(length);
			string.append(layers.get(i));
			for (int j = 0; j < length - layers.get(i).length(); j++) {
				string.append(' ');
			}
			layers.set(i, string.toString());
		}
		for (int i = 0; i < layers.size(); i++) {
			layer = layers.get(i);
			int[] hidden_layer = new int[layer.length()];
			for (int j = 0; j < layer.length(); j++) {
				char character = layer.charAt(j);
				if (character >= '0' && character <= '9') {
					createBall(i, j, character - '0');
				} else if (character == '⇓') {
					int value;
					if ((value = Integer.parseInt(reader.readLine().trim())) != 0) {
						createBall(i, j, value);
					}

				} else if (character == '⇩') {
					for (char value : reader.readLine().toCharArray()) {
						createBall(i, j, value);
					}
				}
			}
			hidden_layers[i] = hidden_layer;
		}

		while (keepRunning()) {
			for (long time = 0; time < delay; time++) {
				try {
					Thread.sleep(1);
				} catch (InterruptedException e) {
					e.printStackTrace();
					time--;
				}
			}
			if (debug) {
				System.out.println(balls);
				String command = reader.readLine();
				if (command.equals("expand")) {
					char[][] chars = new char[Simulator.layers * 2][Simulator.length * 2];
					for (int i = 0; i < layers.size(); i++) {
						for (int j = 0; j < layers.get(i).length(); j++) {
							chars[i * 2][j * 2] = layers.get(i).charAt(j);
							chars[i * 2][j * 2 + 1] = ' ';
							chars[i * 2 + 1][j * 2 + 1] = ' ';
							chars[i * 2 + 1][j * 2] = ' ';
						}
					}
					for (Ball ball : balls.values()) {
						try {
							chars[ball.getLayer() * 2 + 1][ball.getColumn() * 2 + 1] = 'o';
						} catch (ArrayIndexOutOfBoundsException e) {

						}
					}
					for (char[] row : chars) {
						for (char e : row) {
							System.out.print(e);
						}
						System.out.println();
					}
				}
			}
			List<Integer> keys = new ArrayList<>(balls.keySet());
			Collections.sort(keys);
			for (Integer id : keys) {
				Ball ball = balls.get(id);
				if (ball == null) {
				} else if (!valid(ball)) {
					balls.remove(ball.getName());
				} else {
					char space = layers.get(ball.getLayer()).charAt(ball.getColumn());

					if (space == '|') {
						System.out.print(""); /* debug */
					}
				}
			}
		}
	}

	public static boolean emptyLayer(int layer) {
		for (Ball ball : balls.values()) {
			if (ball.getLayer() == layer) {
				return false;
			}
		}
		return true;
	}

	public static boolean valid(Ball ball) {
		return ball.getLayer() >= 0 && ball.getLayer() < layers && ball.getColumn() >= 0 && ball.getColumn() < length;
	}

	public static boolean keepRunning() {
		for (Ball ball : balls.values()) {
			if (ball.getLayer() >= 0 && ball.getLayer() < layers && ball.getColumn() >= 0
					&& ball.getColumn() < length) {
				return true;
			}
		}
		return false;
	}

	public static Ball createBall(int layer, int column, int value) {
		int k = 0;
		while (balls.containsKey(k)) {
			k++;
		}
		Ball ball;
		balls.put(k, ball = new Ball(k, layer, column, value));
		return ball;
	}

	public static final class Ball {
		private int name;
		private int layer;
		private int column;
		private int direction;
		private int levitating;
		private int value;

		public Ball(int name, int layer, int column, int value) {
			this.setName(name);
			this.setLayer(layer);
			this.setColumn(column);
			this.setDirection(0);
			this.setLevitating(-1);
			this.setValue(value);
		}

		public String toString() {
			return "Ball " + getName() + ": [" + getLayer() + ", " + getColumn() + "]: " + getValue() + " (\'"
					+ (char) getValue() + "\')";
		}
	}

	public interface Operator<T, U, R> {
		public R operate(T x, U y);

		@SuppressWarnings("serial")
		Map<Character, Operator<Integer, Integer, Integer>> operators = new HashMap<Character, Operator<Integer, Integer, Integer>>() {
			{
				put('+', (x, y) -> (x + y));
				put('-', (x, y) -> (x - y));
				put('*', (x, y) -> (x * y));
				put('|', (x, y) -> (x == 0 && y == 0) ? 0 : 1);
				put('&', (x, y) -> (x == 0 || y == 0) ? 0 : 1);
			}
		};

		@SuppressWarnings("serial")
		Map<Character, Operator<Integer, Integer, Boolean>> comparators = new HashMap<Character, Operator<Integer, Integer, Boolean>>() {
			{
				put('>', (x, y) -> (x > y));
				put('<', (x, y) -> (x < y));
				put('≥', (x, y) -> (x >= y));
				put('≤', (x, y) -> (x <= y));
				put('=', (x, y) -> (x == y));
			}
		};
	}
}
